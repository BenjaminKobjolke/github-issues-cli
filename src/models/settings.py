"""One immutable description of a single run, validated at the argparse boundary."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from src.constants import LOGGING_VERBOSE, REPO_DIR_SEPARATOR
from src.github import repo_slug


@dataclass(frozen=True)
class Settings:
    """Everything one run needs. Bundled so it is passed as one value, not six."""

    repo: str
    out_dir: Path
    state: str
    limit: int
    force: bool
    verbose: bool

    @property
    def target_dir(self) -> Path:
        """Where this run's markdown files land."""
        return self.out_dir / self.repo.replace("/", REPO_DIR_SEPARATOR)

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "Settings":
        """Validate raw argparse output. Raise ValueError on anything unusable."""
        limit = int(args.limit)
        if limit < 1:
            raise ValueError(f"--limit must be >= 1, got {limit}")

        return cls(
            repo=repo_slug(args.repo),
            out_dir=Path(args.out),
            state=args.state,
            limit=limit,
            force=bool(args.force),
            verbose=args.logging == LOGGING_VERBOSE,
        )
