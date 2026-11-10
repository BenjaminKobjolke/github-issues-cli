"""Canonical `gh` JSON payloads for the unit tests.

Shaped like real `gh issue list --json ...` / `gh issue view --json comments` output, so a
GitHub-side field rename is a single edit here, not a hunt through several test files.
"""

from typing import Any

ISSUE_PAYLOAD: dict[str, Any] = {
    "number": 1,
    "title": "Icons have a low resolution",
    "body": "Compare the two screenshots:\r\n\r\n![shot](https://example.invalid/a.png)\r\n",
    "author": {"id": "MDQ6", "is_bot": False, "login": "mherrmann", "name": "Michael Herrmann"},
    "labels": [
        {"id": "L1", "name": "bug", "description": "", "color": "d93f0b"},
        {"id": "L2", "name": "5 votes", "description": "", "color": "c2e0c6"},
    ],
    "state": "OPEN",
    "createdAt": "2017-03-21T13:04:02Z",
    "updatedAt": "2018-07-31T10:30:10Z",
    "url": "https://github.com/mherrmann/fman/issues/1",
}

COMMENT_PAYLOAD: dict[str, Any] = {
    "author": {"login": "PowerSnail"},
    "authorAssociation": "NONE",
    "body": "Same problem on Linux.\r\nSecond line.",
    "createdAt": "2018-07-21T10:29:50Z",
    "id": "MDEy",
    "url": "https://github.com/mherrmann/fman/issues/1#issuecomment-1",
}


def issue_payload(**overrides: Any) -> dict[str, Any]:
    """A fresh copy of the canonical issue payload, with any field overridden."""
    payload = dict(ISSUE_PAYLOAD)
    payload.update(overrides)
    return payload


def comment_payload(**overrides: Any) -> dict[str, Any]:
    """A fresh copy of the canonical comment payload, with any field overridden."""
    payload = dict(COMMENT_PAYLOAD)
    payload.update(overrides)
    return payload
