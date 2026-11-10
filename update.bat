@echo off
echo Upgrading lock file...
uv lock --upgrade
if errorlevel 1 exit /b 1
echo.
echo Syncing dependencies...
uv sync --all-extras
if errorlevel 1 exit /b 1
echo.
echo Linting...
uv run ruff check .
if errorlevel 1 exit /b 1
echo.
echo Type checking...
uv run mypy src/ main.py
if errorlevel 1 exit /b 1
echo.
echo Running tests...
call "%~dp0tools\run_tests.bat"
if errorlevel 1 exit /b 1
echo.
echo Update complete.
echo NOTE: after a gh upgrade, run the live smoke test to prove the JSON fields still exist:
echo set GITHUB_ISSUES_CLI_LIVE=1 ^&^& uv run pytest tests/integration -m live
