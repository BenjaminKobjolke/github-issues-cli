# github-issues-cli — Architecture

Developer-facing notes. For installation and usage see [`README.md`](../README.md).

The tool is a sibling of `googleplay-cli` and keeps its layout and conventions. This document
covers the parts that are a *decision* rather than a mechanism.

## Module map

```
main.py                     sys.exit(main()) — nothing else
src/constants.py            every literal used more than once. No logic.
src/app_logger.py           AppLogger — the only module that imports `logging`
src/models/issue.py         Issue, Comment — frozen; the gh JSON is normalized here
src/models/settings.py      Settings — frozen; argparse output is validated here
src/github.py               repo_slug(), run_gh(), list_issues(), fetch_comments() — the only module that runs gh
src/markdown.py             Issue -> filename + markdown text. Pure, no I/O.
src/cli.py                  argparse, run() orchestration, skip decision, file writing
```

Dependency direction is one-way: `cli` → `markdown`/`github`/`models` → `constants`/`app_logger`.

**Import cycle, handled like googleplay-cli:** `models/settings.py` imports `repo_slug` from
`github.py`, and `github.py` needs `Settings` only for type hints, so it imports it under
`if TYPE_CHECKING:`. A runtime import of `Settings` in `github.py` breaks the package import.

## Data flow

```
--repo string
   │  repo_slug()                      reject anything that is not github.com or owner/repo
   ▼
Settings (frozen)
   │  list_issues()   gh issue list -R <repo> --state <s> --limit <n> --search sort:created-asc --json ...
   ▼
list[Issue]                            raw dicts stop at Issue.from_api()
   │  per issue: file with that number exists and no --force?  -> skip (no further gh call)
   │  fetch_comments()  gh issue view <n> -R <repo> --json comments
   ▼
issue_filename() / issue_markdown()    pure, no I/O
   ▼
<out>/<owner>__<repo>/<number:05d>-<slug>.md
```

## Design decisions

### Why `gh` and not the REST API

The fman `upstream-issues` skill already reads issues with `gh`, and the user's machine is logged
in. Using the same commands means no token handling, no HTTP client dependency and no pagination
code here: `gh --limit` pages internally, and `gh issue view` returns every comment.

The price is that `gh` must be installed and logged in wherever the tool runs, including the
data-server host.

### Read-only

`github.py` runs only `issue list` and `issue view`. The fman upstream owner asked forks not to
post on the tracker (mherrmann/fman#920); a tool that can only read cannot break that by accident.

### The runner is the test seam

`run(settings, runner=run_gh)` takes the function that runs `gh`. Unit tests check the exact argv
and the JSON handling with a recording runner; the integration test answers with canned JSON so
the real parsing, skipping and writing run without a network.

### The filesystem is the resume state

An issue whose number already has a file is skipped unless `--force` is passed. The check globs
`<number:05d>-*.md`, so a renamed title is not mistaken for a new issue. It runs **before** the
comments call, which keeps a re-run at one `gh issue list` plus one `gh issue view` per new issue.

Known limit, marked with a `shortcut:` comment in `cli.py`: new comments on an issue that already
has a file are not picked up without `--force`. The user chose this over comparing `updatedAt`.

With `--force`, a file for the same number under an old title is removed after the new one is
written, so the folder never holds two files for one issue.

### Zero issues is a valid result

Unlike googleplay-cli, where zero reviews means a broken scraper, a repository with no open issues
is normal. `gh` reports real failures itself (exit code and stderr), which become exit `1`.

### Frontmatter escaping is structural

Titles, authors and labels are third-party text. `issue_markdown()` builds the frontmatter from
one `(key, value)` list rendered by one loop through `_yaml_str()`, the same shape as
googleplay-cli. Do not write a frontmatter field by hand.

## Testing

| Layer | Path | Network |
|---|---|---|
| Unit | `tests/unit/` | never |
| Integration | `tests/integration/test_pipeline.py` | never — gh is stubbed |
| Live smoke | `tests/integration/test_live_smoke.py` | yes, opt-in (`GITHUB_ISSUES_CLI_LIVE=1`) |

The live test reads 3 open issues of `mherrmann/fman`. Run it after a `gh` upgrade.
