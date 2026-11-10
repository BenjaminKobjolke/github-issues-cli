@echo off
REM The live smoke test is skipped here on purpose (needs GITHUB_ISSUES_CLI_LIVE=1),
REM so this run never touches GitHub.
uv run pytest tests/integration -v
exit /b %errorlevel%
