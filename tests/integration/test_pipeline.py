"""Full Settings -> gh -> markdown -> disk pipeline, with the `gh` runner stubbed out.

No network: the injected runner is what `run()` would otherwise use to spawn `gh`. It answers
with canned JSON, so the real parsing runs too. This covers the wiring the unit tests cannot
see: directory creation, the skip-if-exists resume path, --force, exit codes and the result line.
"""

import json
from pathlib import Path

import pytest

from src.cli import run
from src.constants import EXIT_GH_FAILED, EXIT_OK
from src.github import GhError
from src.models.settings import Settings

REPO_DIR = "mherrmann__fman"

ISSUES = [
    {
        "number": 1,
        "title": "Icons have a low resolution",
        "body": "Compare the two screenshots.",
        "author": {"login": "mherrmann"},
        "labels": [{"name": "bug"}],
        "state": "OPEN",
        "createdAt": "2017-03-21T13:04:02Z",
        "updatedAt": "2018-07-31T10:30:10Z",
        "url": "https://github.com/mherrmann/fman/issues/1",
    },
    {
        "number": 2,
        "title": 'Crash: "quotes" here',
        "body": "line one\r\nline two",
        "author": None,
        "labels": [],
        "state": "OPEN",
        "createdAt": "2017-03-22T08:00:00Z",
        "updatedAt": "2017-03-22T08:00:00Z",
        "url": "https://github.com/mherrmann/fman/issues/2",
    },
]

COMMENTS = {
    "1": [{"author": {"login": "alice"}, "body": "Same here.", "createdAt": "2017-04-01T00:00:00Z"}],
    "2": [],
}


class FakeGh:
    """Answers `issue list` and `issue view <n>` like gh does, and counts the calls."""

    def __init__(self, issues: list[dict[str, object]]) -> None:
        self.issues = issues
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str]) -> str:
        self.calls.append(args)
        if args[:2] == ["issue", "list"]:
            return json.dumps(self.issues)
        return json.dumps({"comments": COMMENTS[args[2]]})

    @property
    def view_calls(self) -> int:
        return sum(1 for call in self.calls if call[:2] == ["issue", "view"])


def failing_gh(_args: list[str]) -> str:
    raise GhError("gh issue list failed: HTTP 404: Not Found")


def make_settings(out_dir: Path, force: bool = False) -> Settings:
    return Settings(repo="mherrmann/fman", out_dir=out_dir, state="open", limit=5000, force=force, verbose=False)


def test_run_writes_one_file_per_issue(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run(make_settings(tmp_path), runner=FakeGh(ISSUES))

    assert exit_code == EXIT_OK
    files = sorted(p.name for p in (tmp_path / REPO_DIR).glob("*.md"))
    assert files == ["00001-icons-have-a-low-resolution.md", "00002-crash-quotes-here.md"]
    assert "wrote 2, skipped 0" in capsys.readouterr().out


def test_written_file_has_frontmatter_body_and_comments(tmp_path: Path) -> None:
    run(make_settings(tmp_path), runner=FakeGh(ISSUES))

    first = (tmp_path / REPO_DIR / "00001-icons-have-a-low-resolution.md").read_text(encoding="utf-8")
    second = (tmp_path / REPO_DIR / "00002-crash-quotes-here.md").read_text(encoding="utf-8")

    assert first.startswith("---\nnumber: 1\n")
    assert "### alice — 2017-04-01\n\nSame here.\n" in first
    assert 'title: "Crash: \\"quotes\\" here"' in second
    assert 'author: "ghost"' in second
    assert "line one\nline two" in second


def test_second_run_skips_everything_without_fetching_comments(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run(make_settings(tmp_path), runner=FakeGh(ISSUES))
    capsys.readouterr()
    gh = FakeGh(ISSUES)

    exit_code = run(make_settings(tmp_path), runner=gh)

    assert exit_code == EXIT_OK
    assert "wrote 0, skipped 2" in capsys.readouterr().out
    assert gh.view_calls == 0


def test_force_rewrites_and_drops_the_old_name_of_a_renamed_issue(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run(make_settings(tmp_path), runner=FakeGh(ISSUES))
    capsys.readouterr()
    renamed = [dict(ISSUES[0], title="Icons are blurry"), ISSUES[1]]

    run(make_settings(tmp_path, force=True), runner=FakeGh(renamed))

    assert "wrote 2, skipped 0" in capsys.readouterr().out
    names = sorted(p.name for p in (tmp_path / REPO_DIR).glob("00001-*.md"))
    assert names == ["00001-icons-are-blurry.md"]


def test_zero_issues_is_a_valid_result(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = run(make_settings(tmp_path), runner=FakeGh([]))

    assert exit_code == EXIT_OK
    assert "wrote 0, skipped 0" in capsys.readouterr().out


def test_gh_failure_exits_one(tmp_path: Path) -> None:
    assert run(make_settings(tmp_path), runner=failing_gh) == EXIT_GH_FAILED


def test_run_creates_the_output_directory(tmp_path: Path) -> None:
    nested = tmp_path / "deep" / "nested"
    run(make_settings(nested), runner=FakeGh(ISSUES))

    assert (nested / REPO_DIR).is_dir()
