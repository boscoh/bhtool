#!/usr/bin/env python3

"""Shared utilities for btools scripts."""

import os
import platform
import subprocess
import sys
from collections.abc import Iterator
from path import Path


def run(cmd: str, env=None) -> None:
    """Run a shell command, printing it first. Exits on failure.

    :param cmd: Shell command to run
    :param env: Optional environment variables dict
    """
    print(f">> {cmd}")
    result = subprocess.run(cmd, shell=True, env=env)
    if result.returncode != 0:
        sys.exit(result.returncode)


def run_output(cmd: str) -> str:
    """Run a shell command and return its output as text.

    :param cmd: Shell command to run
    :return: stdout+stderr output, or empty string on error
    """
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return result.decode("utf-8", errors="ignore")
    except subprocess.CalledProcessError:
        return ""


def open_path(filepath: str) -> None:
    """Open a path with the platform default handler (Finder, explorer, xdg-open)."""
    p = Path(filepath)
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["open", p], check=False)
    elif system == "Windows":
        os.startfile(p)
    else:
        subprocess.run(["xdg-open", p], check=False)


def walk_paths(root: str) -> Iterator[Path]:
    """Depth-first walk of ``root`` (files and dirs), using ``path.Path.walk``."""
    base = Path(root)
    if base.is_dir():
        yield from base.walk()
