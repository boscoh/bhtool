#!/usr/bin/env python3

"""Bump version in pyproject.toml, commit, push, and optionally publish to PyPI."""

import re
import sys
from path import Path
from typing import Literal

from bhtool.utils import run


def bumpver(
    part: Literal["major", "minor", "patch"] | None = None, *, publish: bool = True
):
    """Bump version in pyproject.toml, commit, push, and publish."""
    if part is None:
        from bhtool.cli import app

        app["bumpver"].help_print()
        return

    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        print("Could not find pyproject.toml")
        sys.exit(1)

    text = pyproject.read_text()
    match = re.search(r'^version = "(\d+)\.(\d+)\.(\d+)"', text, re.MULTILINE)
    if not match:
        print("Could not find version in pyproject.toml")
        sys.exit(1)

    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    print(f"Current version: {major}.{minor}.{patch}")

    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    pyproject.write_text(text.replace(match.group(0), f'version = "{new_version}"'))
    print(f"Version bumped to {new_version}")

    run(f'git commit -am "Bump version to {new_version}"')
    run("git push")

    if publish:
        run("uv build")
        run(f"uv publish dist/*-{new_version}*")
