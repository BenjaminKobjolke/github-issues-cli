# Version
3

# Coding Rules (Pointer)

This project's rules live in two files in the project root:

- `CODING_RULES.md` — code quality and conventions. BINDING for all code work in
  this repository, always.
- `IMPLEMENTATION_FLOW.md` — the end-to-end flow to follow when planning and
  implementing a change (checks, gates, Definition of Done).

MANDATORY: Before writing or editing ANY code, you MUST Read BOTH files in full
**in the current session**. Do not rely on memory of a previous session, a
summary, or partial reads.

If you are about to make a code change and have not read both files in this
session: STOP, read them, then continue.

An external tool may orchestrate the implementation itself. When a skill or run
states that the implementation is orchestrated, ignore `IMPLEMENTATION_FLOW.md`
entirely — the orchestrator runs those steps as its own phases. `CODING_RULES.md`
stays binding either way.

Next to `CODING_RULES.md`, apply also writes `CODING_RULES_PLAN.md`,
`CODING_RULES_REVIEW.md` and `CODING_RULES_CODE.md`. When an orchestrator's run
instructions name one of these step files, that file replaces `CODING_RULES.md`
for that run; without such an instruction, `CODING_RULES.md` stays binding in full.

Do not inline rules back into this file and do not use `@import` for either file —
they are intentionally referenced, not imported.

This project's code directory is src/ (graphify builds and queries are scoped to it).

## Read-only GitHub

This tool only reads GitHub. `src/github.py` runs `gh issue list` and `gh issue view` and
nothing else. Never add a `gh` call that writes (comment, close, edit, react, PR).

## Testing

```bash
tools\run_tests.bat               # unit tests, no network
tools\run_integration_tests.bat   # pipeline with gh stubbed, no network
```

The live smoke test needs `GITHUB_ISSUES_CLI_LIVE=1` and a logged-in `gh`.

## Code Analysis

Run the changed-files analyzer after implementing a feature or fixing a bug:

```bash
powershell -Command "cd 'D:\GIT\BenjaminKobjolke\github-issues-cli'; cmd /c '.\tools\analyze_changed_and_new_files.bat'"
```

It filters findings to Python files that are new or modified against Git `HEAD`, including untracked files. Use `tools/analyze_code.bat` for a full project analysis.

Reports are written to `code_analysis_results/` as per-rule CSV files. A missing CSV means that analyzer found no findings. Fix reported issues before committing.
