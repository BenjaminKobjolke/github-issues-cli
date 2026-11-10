from src.markdown import issue_filename, issue_glob, issue_markdown
from src.models.issue import Comment, Issue
from tests.unit.payloads import comment_payload, issue_payload


def make_issue(**overrides: object) -> Issue:
    return Issue.from_api(issue_payload(**overrides))


def test_filename_is_padded_number_plus_slug() -> None:
    assert issue_filename(make_issue()) == "00001-icons-have-a-low-resolution.md"


def test_filename_slug_drops_unsafe_characters() -> None:
    issue = make_issue(number=920, title='Crash: "C:\\Temp" / *.txt?')
    assert issue_filename(issue) == "00920-crash-c-temp-txt.md"


def test_filename_slug_is_truncated() -> None:
    name = issue_filename(make_issue(title="word " * 40))
    slug = name[len("00001-") : -len(".md")]
    assert len(slug) <= 50
    assert not slug.endswith("-")


def test_filename_falls_back_when_the_title_has_no_usable_characters() -> None:
    assert issue_filename(make_issue(title="???")) == "00001-issue.md"


def test_glob_matches_the_filename_whatever_the_title() -> None:
    issue = make_issue()
    renamed = make_issue(title="A completely different title")
    assert issue_glob(issue) == "00001-*.md"
    assert issue_glob(renamed) == issue_glob(issue)


def test_markdown_frontmatter() -> None:
    text = issue_markdown(make_issue(), [])

    assert text.startswith("---\n")
    assert "number: 1\n" in text
    assert 'title: "Icons have a low resolution"\n' in text
    assert 'state: "OPEN"\n' in text
    assert 'author: "mherrmann"\n' in text
    assert 'created: "2017-03-21"\n' in text
    assert 'updated: "2018-07-31"\n' in text
    assert 'labels: "bug, 5 votes"\n' in text
    assert 'url: "https://github.com/mherrmann/fman/issues/1"\n' in text


def test_markdown_escapes_untrusted_frontmatter_text() -> None:
    text = issue_markdown(make_issue(title='Say "hi": now\nplease'), [])
    assert 'title: "Say \\"hi\\": now please"\n' in text


def test_markdown_body_uses_unix_line_endings() -> None:
    text = issue_markdown(make_issue(), [])

    assert "\r" not in text
    assert "# Icons have a low resolution\n\nCompare the two screenshots:\n\n![shot]" in text


def test_markdown_without_comments_has_no_comments_section() -> None:
    assert "## Comments" not in issue_markdown(make_issue(), [])


def test_markdown_lists_comments_in_order() -> None:
    first = Comment.from_api(comment_payload())
    second = Comment.from_api(comment_payload(author={"login": "bob"}, body="me too", createdAt="2019-01-02T00:00:00Z"))

    text = issue_markdown(make_issue(), [first, second])

    assert "## Comments\n\n### PowerSnail — 2018-07-21\n\nSame problem on Linux.\nSecond line.\n" in text
    assert text.index("PowerSnail") < text.index("### bob — 2019-01-02")
    assert text.endswith("me too\n")
