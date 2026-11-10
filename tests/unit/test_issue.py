from datetime import datetime, timezone

import pytest

from src.models.issue import Comment, Issue
from tests.unit.payloads import comment_payload, issue_payload


def test_from_api_reads_every_field() -> None:
    issue = Issue.from_api(issue_payload())

    assert issue.number == 1
    assert issue.title == "Icons have a low resolution"
    assert issue.author == "mherrmann"
    assert issue.labels == ("bug", "5 votes")
    assert issue.state == "OPEN"
    assert issue.created_at == datetime(2017, 3, 21, 13, 4, 2, tzinfo=timezone.utc)
    assert issue.updated_at == datetime(2018, 7, 31, 10, 30, 10, tzinfo=timezone.utc)
    assert issue.url == "https://github.com/mherrmann/fman/issues/1"


def test_from_api_requires_a_number() -> None:
    with pytest.raises(ValueError):
        Issue.from_api(issue_payload(number=None))


def test_from_api_rejects_a_bool_number() -> None:
    with pytest.raises(ValueError):
        Issue.from_api(issue_payload(number=True))


def test_from_api_requires_a_created_date() -> None:
    with pytest.raises(ValueError):
        Issue.from_api(issue_payload(createdAt="not a date"))


def test_from_api_names_a_deleted_author_ghost() -> None:
    # GitHub returns author null for deleted accounts and shows them as "ghost".
    assert Issue.from_api(issue_payload(author=None)).author == "ghost"


def test_from_api_tolerates_missing_optional_fields() -> None:
    issue = Issue.from_api(issue_payload(body=None, labels=None, updatedAt=None))

    assert issue.body == ""
    assert issue.labels == ()
    assert issue.updated_at == issue.created_at


def test_comment_from_api_reads_every_field() -> None:
    comment = Comment.from_api(comment_payload())

    assert comment.author == "PowerSnail"
    assert comment.body == "Same problem on Linux.\r\nSecond line."
    assert comment.created_at == datetime(2018, 7, 21, 10, 29, 50, tzinfo=timezone.utc)


def test_comment_from_api_requires_a_created_date() -> None:
    with pytest.raises(ValueError):
        Comment.from_api(comment_payload(createdAt=None))


def test_issue_is_frozen() -> None:
    issue = Issue.from_api(issue_payload())
    with pytest.raises(Exception):
        issue.title = "changed"  # type: ignore[misc]
