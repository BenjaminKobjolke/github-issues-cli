"""Pins dataserver-tool.json to the data-server external-tool contract (no network)."""

import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "dataserver-tool.json"
NAME_PATTERN = re.compile(r"^[a-z0-9_-]{1,64}$")


def manifest() -> dict[str, object]:
    loaded: dict[str, object] = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return loaded


def test_manifest_name_matches_the_contract_regex() -> None:
    assert NAME_PATTERN.match(str(manifest()["name"]))


def test_manifest_has_a_description() -> None:
    assert str(manifest()["description"]).strip()


def test_manifest_command_is_an_argv_list_of_strings_with_placeholders() -> None:
    command = manifest()["command"]
    assert isinstance(command, list)
    assert all(isinstance(arg, str) for arg in command)
    assert "{url}" in command
    assert "{out}" in command


def test_manifest_check_command_exits_zero() -> None:
    check_command = manifest()["check_command"]
    assert isinstance(check_command, list)
    assert all(isinstance(arg, str) for arg in check_command)
    result = subprocess.run(check_command, cwd=REPO_ROOT, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stderr.decode(errors="replace")
