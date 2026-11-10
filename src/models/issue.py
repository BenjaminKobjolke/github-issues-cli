"""One GitHub issue and its comments, normalized at the `gh` JSON boundary.

The raw `gh` dicts never leave this module. Issue text is untrusted third-party data, and a
field rename in `gh` must fail here rather than read as `None` in the markdown writer.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.constants import GHOST_AUTHOR


@dataclass(frozen=True)
class Comment:
    """A single issue comment."""

    author: str
    body: str
    created_at: datetime

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> "Comment":
        """Build from one `gh issue view --json comments` entry. Raise ValueError if unusable."""
        return cls(
            author=_author(raw.get("author")),
            body=_text(raw.get("body")),
            created_at=_required_date(raw.get("createdAt"), "comment"),
        )


@dataclass(frozen=True)
class Issue:
    """A single issue, without its comments (they come from a second `gh` call)."""

    number: int
    title: str
    body: str
    author: str
    labels: tuple[str, ...]
    state: str
    created_at: datetime
    updated_at: datetime
    url: str

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> "Issue":
        """Build from one `gh issue list --json ...` row. Raise ValueError if unusable."""
        number = raw.get("number")
        if isinstance(number, bool) or not isinstance(number, int):
            raise ValueError(f"issue is missing a usable 'number': {number!r}")

        created_at = _required_date(raw.get("createdAt"), f"issue #{number}")
        labels = raw.get("labels") or []

        return cls(
            number=number,
            title=_text(raw.get("title")),
            body=_text(raw.get("body")),
            author=_author(raw.get("author")),
            labels=tuple(_text(label.get("name")) for label in labels if isinstance(label, dict)),
            state=_text(raw.get("state")),
            created_at=created_at,
            updated_at=_optional_date(raw.get("updatedAt")) or created_at,
            url=_text(raw.get("url")),
        )


def _text(value: object) -> str:
    return "" if value is None else str(value)


def _author(value: object) -> str:
    """gh returns `author: null` for deleted accounts; GitHub shows those as 'ghost'."""
    if isinstance(value, dict) and value.get("login"):
        return str(value["login"])
    return GHOST_AUTHOR


def _optional_date(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _required_date(value: object, what: str) -> datetime:
    parsed = _optional_date(value)
    if parsed is None:
        raise ValueError(f"{what} has no usable 'createdAt': {value!r}")
    return parsed
