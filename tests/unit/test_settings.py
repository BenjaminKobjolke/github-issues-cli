import argparse
from pathlib import Path

import pytest

from src.constants import LOGGING_ERROR, LOGGING_VERBOSE
from src.models.settings import Settings


def namespace(**overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "repo": "https://github.com/mherrmann/fman",
        "out": "./issues",
        "state": "open",
        "limit": 5000,
        "force": False,
        "logging": LOGGING_ERROR,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_from_args_resolves_the_repo_slug() -> None:
    assert Settings.from_args(namespace()).repo == "mherrmann/fman"


def test_from_args_builds_a_path_for_the_output_dir() -> None:
    assert Settings.from_args(namespace(out="./out")).out_dir == Path("./out")


def test_from_args_maps_the_logging_flag_to_verbose() -> None:
    assert Settings.from_args(namespace(logging=LOGGING_VERBOSE)).verbose is True
    assert Settings.from_args(namespace(logging=LOGGING_ERROR)).verbose is False


def test_from_args_rejects_a_limit_below_one() -> None:
    with pytest.raises(ValueError):
        Settings.from_args(namespace(limit=0))


def test_from_args_rejects_a_foreign_host() -> None:
    with pytest.raises(ValueError):
        Settings.from_args(namespace(repo="https://gitlab.com/owner/repo"))


def test_target_dir_flattens_owner_and_repo(tmp_path: Path) -> None:
    settings = Settings.from_args(namespace(out=str(tmp_path)))
    assert settings.target_dir == tmp_path / "mherrmann__fman"


def test_settings_is_frozen() -> None:
    settings = Settings.from_args(namespace())
    with pytest.raises(Exception):
        settings.state = "all"  # type: ignore[misc]
