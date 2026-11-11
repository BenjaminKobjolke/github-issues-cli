"""Argument parsing and run orchestration."""

from __future__ import annotations

import argparse

from src.app_logger import AppLogger
from src.constants import (
    DEFAULT_LIMIT,
    DEFAULT_OUT_DIR,
    DEFAULT_STATE,
    DONE_DIR,
    EXIT_BAD_INPUT,
    EXIT_GH_FAILED,
    EXIT_OK,
    FILE_ENCODING,
    LOGGING_ERROR,
    LOGGING_VERBOSE,
    STATE_CHOICES,
)
from src.github import GhError, GhRunner, fetch_comments, list_issues, run_gh
from src.markdown import issue_filename, issue_glob, issue_markdown
from src.models.settings import Settings


def create_argument_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        prog="github-issues-cli",
        description="Download the issues of a GitHub repository to markdown files (via gh).",
    )
    parser.add_argument("--repo", required=True, help="GitHub repository URL or owner/repo")
    parser.add_argument("--out", default=DEFAULT_OUT_DIR, help=f"output root (default: {DEFAULT_OUT_DIR})")
    parser.add_argument(
        "--state", choices=STATE_CHOICES, default=DEFAULT_STATE, help=f"issue state (default: {DEFAULT_STATE})"
    )
    parser.add_argument(
        "--limit", type=int, default=DEFAULT_LIMIT, help=f"maximum number of issues (default: {DEFAULT_LIMIT})"
    )
    parser.add_argument("--force", action="store_true", help="rewrite files that already exist")
    parser.add_argument(
        "--logging",
        choices=[LOGGING_ERROR, LOGGING_VERBOSE],
        default=LOGGING_ERROR,
        help=f"log verbosity (default: {LOGGING_ERROR})",
    )
    return parser


def run(settings: Settings, runner: GhRunner = run_gh) -> int:
    """Fetch, write, and return an exit code. `runner` is the test injection seam for `gh`."""
    target_dir = settings.target_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    try:
        for issue in list_issues(settings, runner):
            existing = list(target_dir.glob(issue_glob(issue)))
            done = list((target_dir / DONE_DIR).glob(issue_glob(issue)))
            # The filesystem is the resume state, and skipping happens before the comments
            # call, so a re-run costs one list call plus one view call per new issue.
            # shortcut: new comments on an issue that already has a file are missed until --force.
            # A done issue stays skipped with --force so it never re-enters the review queue.
            if done or (existing and not settings.force):
                AppLogger.info(f"skipping existing {(done or existing)[0].name}")
                skipped += 1
                continue

            comments = fetch_comments(settings, issue.number, runner)
            target = target_dir / issue_filename(issue)
            target.write_text(issue_markdown(issue, comments), encoding=FILE_ENCODING)
            for old in existing:
                if old != target:  # the title changed since the last run
                    old.unlink()
            AppLogger.info(f"wrote {target.name}")
            written += 1
    except GhError as error:
        AppLogger.error(str(error))
        return EXIT_GH_FAILED

    print(f"wrote {written}, skipped {skipped} -> {target_dir}")
    return EXIT_OK


def main() -> int:
    """Entry point. Returns the process exit code."""
    args = create_argument_parser().parse_args()

    try:
        settings = Settings.from_args(args)
    except ValueError as error:
        AppLogger.configure(verbose=False)
        AppLogger.error(str(error))
        return EXIT_BAD_INPUT

    AppLogger.configure(verbose=settings.verbose)
    return run(settings)
