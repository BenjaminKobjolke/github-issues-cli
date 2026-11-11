# github-issues-cli

Downloads the issues of a GitHub repository, with all their comments, and writes each one to its
own markdown file with YAML frontmatter. Point it at a repository URL (or `owner/repo`), give it
an output folder, and it fills that folder with one `.md` per issue, ready to drop into Obsidian,
grep, or feed to something else.

It reads GitHub through the [GitHub CLI](https://cli.github.com/) (`gh`), with the same commands
the fman `upstream-issues` skill uses. It only reads: it never comments, closes or edits anything.

## Requirements

- Python `>=3.11,<3.13`
- [`uv`](https://docs.astral.sh/uv/)
- [`gh`](https://cli.github.com/), logged in (`gh auth login`) or with `GH_TOKEN` set. Public
  repositories still need a login: `gh` refuses to run without one.
- Windows-friendly (the batch files assume it), but nothing in `src/` is platform-specific

There are no runtime Python dependencies; only the standard library and `gh`.

## Installation

```
install.bat
```

That runs `uv sync --all-extras` and then the unit tests, so a green install is also a proven one.

## Usage

```
start.bat --repo https://github.com/mherrmann/fman --out ./issues
```

`--repo` also accepts `owner/repo`, and any URL inside the repository:

```
start.bat --repo mherrmann/fman --state all --limit 50
start.bat --repo https://github.com/mherrmann/fman/issues/920
```

| Flag | Default | Note |
|---|---|---|
| `--repo` | required | `https://github.com/owner/repo[/...]` or `owner/repo` |
| `--out` | `./issues` | output root |
| `--state` | `open` | `open`, `closed` or `all` |
| `--limit` | `5000` | maximum number of issues; `gh`'s own default would be 30 |
| `--force` | off | rewrite files that already exist in the repo folder; never touches `done/` |
| `--logging` | `error` | `error` or `verbose` |

Output on success is a single line:

```
wrote 12, skipped 340 -> issues\mherrmann__fman
```

Exit codes: `0` success (zero issues is a valid result), `1` `gh` failed (not installed, not
logged in, repository not found; the reason is logged), `2` bad input.

Pull requests are not included: `gh issue list` leaves them out.

A sample output file:

```markdown
---
number: 1
title: "Icons have a low resolution"
state: "OPEN"
author: "mherrmann"
created: "2017-03-21"
updated: "2018-07-31"
labels: "bug, mac, 5 votes"
url: "https://github.com/mherrmann/fman/issues/1"
---

# Icons have a low resolution

Compare the two screenshots ...

## Comments

### PowerSnail — 2018-07-21

Just reporting that I observe the same problem in Linux.
```

Images stay as links to GitHub; they are not downloaded. A deleted account shows as `ghost`,
as on GitHub.

## Output layout

```
<out>/<owner>__<repo>/<number:05d>-<title-slug>.md
```

The padded number makes the folder sort by issue number. The slug is the lower-cased title with
everything outside `a-z0-9` turned into `-`, at most 50 characters.

**Resume is just the filesystem.** An issue that already has a file (matched by its number, so a
renamed title does not count as new) is skipped, and its comments are not fetched again. A file for
the issue in the repo folder's `done/` subfolder also counts as already downloaded, including with
`--force`; nothing inside `done/` is ever rewritten, renamed or deleted. A re-run therefore costs
one `gh issue list` call plus one `gh issue view` per new issue.

The flip side: new comments on an issue that already has a file are not picked up. Pass
`--force` to rewrite existing files in the repo folder; it also removes the old file of an issue
whose title changed.

## Data-server integration

This repo ships `dataserver-tool.json`, the external-tool manifest for the AI Chat data server
(the standard is documented in `ai-chat-data-server/docs/EXTERNAL_TOOLS.md`). Clients call the
data server with `tool: "github-issues"` plus a repository URL; the server runs this CLI by
config only, zips what it wrote and returns a download link.

- The host running the data server needs a logged-in `gh` (or `GH_TOKEN`), or every call exits `1`.
- `--state` and `--limit` stay at their defaults: open issues, up to 5000.
- A non-GitHub URL exits `2` before `gh` runs.
- `tests/unit/test_manifest.py` pins the manifest to the contract.

## Development

Module map and design decisions: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

```
tools\run_tests.bat               unit tests (no network)
tools\run_integration_tests.bat   integration tests (no network, gh is stubbed)
update.bat                        upgrade deps, then ruff + mypy + tests
```

A bare `uv run pytest` runs the unit tests only (`testpaths = ["tests/unit"]`). Every test has a
120-second limit (`timeout = 120` via pytest-timeout).

The live smoke test is the only thing that reaches GitHub, and it is opt-in:

```
set GITHUB_ISSUES_CLI_LIVE=1
uv run pytest tests/integration -v -m live
```

## License

MIT
