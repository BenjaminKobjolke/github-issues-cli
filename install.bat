@echo off
where uv >nul 2>nul
if errorlevel 1 (
    echo uv is not installed. See https://docs.astral.sh/uv/getting-started/installation/
    exit /b 1
)
echo Installing dependencies...
uv sync --all-extras
if errorlevel 1 (
    echo Installation failed.
    exit /b 1
)
echo.
echo Running tests...
call "%~dp0tools\run_tests.bat"
if errorlevel 1 (
    echo Tests failed.
    exit /b 1
)
echo.
echo Installation complete.
