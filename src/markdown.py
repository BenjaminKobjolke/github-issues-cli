"""Issue -> filename and markdown text. Pure functions, no I/O — that is what makes them testable."""

from __future__ import annotations

import re
from datetime import datetime

from src.constants import (
    DATE_FORMAT,
    ISSUE_NUMBER_WIDTH,
    MARKDOWN_SUFFIX,
    SLUG_FALLBACK,
    SLUG_MAX_LEN,
    SLUG_UNSAFE_CHARS,
)
from src.models.issue import Comment, Issue


def issue_filename(issue: Issue) -> str:
    """'00001-icons-have-a-low-resolution.md'."""
    return f"{_number_prefix(issue)}-{_slug(issue.title)}{MARKDOWN_SUFFIX}"


def issue_glob(issue: Issue) -> str:
    """Matches this issue's file whatever its title was when it was written."""
    return f"{_number_prefix(issue)}-*{MARKDOWN_SUFFIX}"


def issue_markdown(issue: Issue, comments: list[Comment]) -> str:
    """YAML frontmatter, the issue body, then every comment."""
    fields: list[tuple[str, object]] = [
        ("number", issue.number),
        ("title", issue.title),
        ("state", issue.state),
        ("author", issue.author),
        ("created", _date(issue.created_at)),
        ("updated", _date(issue.updated_at)),
        ("labels", ", ".join(issue.labels)),
        ("url", issue.url),
    ]

    lines = ["---"]
    lines.extend(f"{key}: {_yaml_value(value)}" for key, value in fields)
    lines.append("---")
    lines.append("")
    lines.append(f"# {_one_line(issue.title)}")
    lines.append("")
    lines.append(_body(issue.body))

    if comments:
        lines.append("")
        lines.append("## Comments")
        for comment in comments:
            lines.append("")
            lines.append(f"### {comment.author} — {_date(comment.created_at)}")
            lines.append("")
            lines.append(_body(comment.body))

    return "\n".join(lines) + "\n"


def _number_prefix(issue: Issue) -> str:
    return f"{issue.number:0{ISSUE_NUMBER_WIDTH}d}"


def _slug(title: str) -> str:
    """Windows-safe, lower-case title. Characters like `:` `"` `*` `?` are illegal in filenames."""
    slug = re.sub(SLUG_UNSAFE_CHARS, "-", title.lower()).strip("-")
    return slug[:SLUG_MAX_LEN].rstrip("-") or SLUG_FALLBACK


def _date(value: datetime) -> str:
    return value.strftime(DATE_FORMAT)


def _body(text: str) -> str:
    """GitHub stores bodies with CRLF; the files use LF like the rest of the markdown."""
    return text.replace("\r\n", "\n").replace("\r", "\n").strip()


def _one_line(text: str) -> str:
    return text.replace("\r", " ").replace("\n", " ")


def _yaml_value(value: object) -> str:
    """Render one frontmatter value. Ints bare, everything else as an escaped string."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return _yaml_str(value)


def _yaml_str(value: object) -> str:
    """Quote and escape a string for YAML.

    Titles, author names and labels are third-party free text containing quotes, colons and
    newlines, so nothing reaches the frontmatter without passing through here. Building the
    frontmatter from one (key, value) loop is what guarantees that.
    """
    text = "" if value is None else str(value)
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{_one_line(escaped)}"'
