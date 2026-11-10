import json
from pathlib import Path

import pytest

from src.github import GhError, fetch_comments, list_issues, repo_slug, run_gh
from src.models.settings import Settings
from tests.unit.payloads import comment_payload, issue_payload


def make_settings(state: str = "open", limit: int = 5000) -> Settings:
    return Settings(repo="mherrmann/fman", out_dir=Path("."), state=state, limit=limit, force=False, verbose=False)


class RecordingRunner:
    """Stands in for `gh`: records each argv and returns a canned stdout."""

    def __init__(self, stdout: str) -> None:
        self.stdout = stdout
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str]) -> str:
        self.calls.append(args)
        return self.stdout


@pytest.mark.parametrize(
    "value",
    [
        "mherrmann/fman",
        "  mherrmann/fman  ",
        "https://github.com/mherrmann/fman",
        "https://github.com/mherrmann/fman/",
        "https://github.com/mherrmann/fman.git",
        "https://github.com/mherrmann/fman/issues",
        "https://github.com/mherrmann/fman/issues/920",
        "http://www.github.com/mherrmann/fman",
    ],
)
def test_repo_slug_accepts_urls_and_slugs(value: str) -> None:
    assert repo_slug(value) == "mherrmann/fman"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "fman",
        "https://github.com/mherrmann",
        "https://gitlab.com/mherrmann/fman",
        "https://github.com.evil.example/mherrmann/fman",
        "owner/repo/extra",
        "own er/repo",
        "../etc",
    ],
)
def test_repo_slug_rejects_anything_else(value: str) -> None:
    with pytest.raises(ValueError):
        repo_slug(value)


def test_list_issues_runs_the_skill_command() -> None:
    runner = RecordingRunner("[]")

    list_issues(make_settings(state="all", limit=50), runner)

    assert runner.calls == [
        [
            "issue",
            "list",
            "-R",
            "mherrmann/fman",
            "--state",
            "all",
            "--limit",
            "50",
            "--search",
            "sort:created-asc",
            "--json",
            "number,title,body,author,labels,state,createdAt,updatedAt,url",
        ]
    ]


def test_list_issues_parses_every_row() -> None:
    runner = RecordingRunner(json.dumps([issue_payload(), issue_payload(number=2, title="Second")]))

    issues = list_issues(make_settings(), runner)

    assert [issue.number for issue in issues] == [1, 2]


def test_list_issues_skips_an_unreadable_row() -> None:
    runner = RecordingRunner(json.dumps([issue_payload(number=None), issue_payload(number=2)]))

    assert [issue.number for issue in list_issues(make_settings(), runner)] == [2]


def test_list_issues_rejects_output_that_is_not_a_list() -> None:
    with pytest.raises(GhError):
        list_issues(make_settings(), RecordingRunner('{"message": "nope"}'))


def test_list_issues_rejects_output_that_is_not_json() -> None:
    with pytest.raises(GhError):
        list_issues(make_settings(), RecordingRunner("not json"))


def test_fetch_comments_runs_issue_view() -> None:
    runner = RecordingRunner('{"comments": []}')

    fetch_comments(make_settings(), 920, runner)

    assert runner.calls == [["issue", "view", "920", "-R", "mherrmann/fman", "--json", "comments"]]


def test_fetch_comments_parses_comments_in_order() -> None:
    payload = {"comments": [comment_payload(), comment_payload(author={"login": "bob"})]}

    comments = fetch_comments(make_settings(), 1, RecordingRunner(json.dumps(payload)))

    assert [comment.author for comment in comments] == ["PowerSnail", "bob"]


def test_fetch_comments_rejects_output_without_a_comment_list() -> None:
    with pytest.raises(GhError):
        fetch_comments(make_settings(), 1, RecordingRunner("{}"))


def test_run_gh_reports_a_missing_executable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.github.GH_EXECUTABLE", "gh-binary-that-does-not-exist")
    with pytest.raises(GhError, match="not found"):
        run_gh(["--version"])
