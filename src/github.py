"""GitHub access through the `gh` CLI: turn user input into `owner/repo`, and read issues.

The only module that runs `gh`. Strictly read-only: `issue list` and `issue view`, the same
commands the fman `upstream-issues` skill uses.
"""

from __future__ import annotations

import json
import re
import subprocess
from typing import TYPE_CHECKING, Any, Callable
from urllib.parse import urlparse

from src.app_logger import AppLogger
from src.constants import (
    FILE_ENCODING,
    GH_COMMENT_FIELDS,
    GH_EXECUTABLE,
    GH_ISSUE_FIELDS,
    GH_SORT_SEARCH,
    GIT_SUFFIX,
    GITHUB_HOSTS,
    REPO_SLUG_PATTERN,
)
from src.models.issue import Comment, Issue

if TYPE_CHECKING:  # Settings imports repo_slug from here, so keep this import type-only.
    from src.models.settings import Settings

GhRunner = Callable[[list[str]], str]


class GhError(Exception):
    """`gh` could not run, failed, or answered with something that is not the expected JSON."""


def repo_slug(url_or_slug: str) -> str:
    """Accept a GitHub URL inside a repository, or `owner/repo`; return `owner/repo`."""
    candidate = url_or_slug.strip()
    if not candidate:
        raise ValueError("no repository URL or owner/repo given")

    parsed = urlparse(candidate)
    if parsed.scheme in ("http", "https"):
        if parsed.hostname not in GITHUB_HOSTS:
            raise ValueError(f"not a GitHub URL: {url_or_slug!r}")
        parts = [part for part in parsed.path.split("/") if part]
        candidate = "/".join(parts[:2])
        candidate = candidate.removesuffix(GIT_SUFFIX)

    # Also rejects "..", so the slug can never climb out of --out as a folder name.
    if not re.match(REPO_SLUG_PATTERN, candidate) or ".." in candidate:
        raise ValueError(f"cannot read owner/repo from {url_or_slug!r}")
    return candidate


def run_gh(args: list[str]) -> str:
    """Run `gh <args>` and return its stdout. Raise GhError with gh's own message on failure."""
    try:
        result = subprocess.run(
            [GH_EXECUTABLE, *args],
            capture_output=True,
            text=True,
            encoding=FILE_ENCODING,
            errors="replace",
            check=False,
        )
    except FileNotFoundError as error:
        raise GhError(f"'{GH_EXECUTABLE}' not found; install the GitHub CLI: https://cli.github.com/") from error

    if result.returncode != 0:
        raise GhError(f"gh {' '.join(args[:2])} failed: {result.stderr.strip()}")
    return result.stdout


def list_issues(settings: "Settings", runner: GhRunner) -> list[Issue]:
    """Every issue of the repository in the requested state, oldest first."""
    AppLogger.info(f"listing {settings.state} issues of {settings.repo} (limit {settings.limit})")
    rows = _json(
        runner(
            [
                "issue",
                "list",
                "-R",
                settings.repo,
                "--state",
                settings.state,
                "--limit",
                str(settings.limit),
                "--search",
                GH_SORT_SEARCH,
                "--json",
                GH_ISSUE_FIELDS,
            ]
        )
    )
    if not isinstance(rows, list):
        raise GhError(f"gh issue list returned {type(rows).__name__}, expected a list")

    issues: list[Issue] = []
    for row in rows:
        try:
            issues.append(Issue.from_api(row))
        except (ValueError, AttributeError) as error:
            # One odd row must not abort a run over hundreds of issues.
            AppLogger.warning(f"skipping unreadable issue: {error}")
    AppLogger.info(f"listed {len(issues)} issues ({len(rows)} rows)")
    return issues


def fetch_comments(settings: "Settings", number: int, runner: GhRunner) -> list[Comment]:
    """All comments of one issue, in the order GitHub shows them."""
    payload = _json(runner(["issue", "view", str(number), "-R", settings.repo, "--json", GH_COMMENT_FIELDS]))
    rows = payload.get(GH_COMMENT_FIELDS) if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise GhError(f"gh issue view {number} returned no comment list")

    comments: list[Comment] = []
    for row in rows:
        try:
            comments.append(Comment.from_api(row))
        except (ValueError, AttributeError) as error:
            AppLogger.warning(f"skipping unreadable comment on #{number}: {error}")
    return comments


def _json(stdout: str) -> Any:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as error:
        raise GhError(f"gh returned invalid JSON: {error}") from error
