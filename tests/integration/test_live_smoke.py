"""Opt-in smoke test against the real GitHub, through the installed and logged-in `gh`.

Skipped unless GITHUB_ISSUES_CLI_LIVE=1, so no suite — not even
tools/run_integration_tests.bat — reaches GitHub unattended. Run it by hand after a `gh`
upgrade: that is the only thing that proves the JSON fields still exist.
"""

import os
from pathlib import Path

import pytest

from src.cli import run
from src.constants import EXIT_OK
from src.models.settings import Settings

LIVE_REPO = "mherrmann/fman"
LIVE_LIMIT = 3

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.getenv("GITHUB_ISSUES_CLI_LIVE") != "1",
        reason="live test: set GITHUB_ISSUES_CLI_LIVE=1 to run it",
    ),
]


def test_live_fetch_writes_files(tmp_path: Path) -> None:
    settings = Settings(repo=LIVE_REPO, out_dir=tmp_path, state="open", limit=LIVE_LIMIT, force=False, verbose=True)

    assert run(settings) == EXIT_OK
    assert len(list(settings.target_dir.glob("*.md"))) == LIVE_LIMIT
