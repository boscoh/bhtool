#!/usr/bin/env python3

"""Unified bhtool CLI (`b` and `bhtool` on PATH)."""

from typing import Literal

from cyclopts import App

app = App(name="bhtool", help="boscoh tools")


@app.command(name="run")
def run(*params: str):
    """Open macOS applications by partial name match."""
    if not params:
        app["run"].help_print()
        return
    from bhtool.run import run

    run(*params)


@app.command
def bumpver(
    part: Literal["major", "minor", "patch"] | None = None, *, publish: bool = True
):
    """Bump version in pyproject.toml, commit, push, and optionally publish to PyPI."""
    from bhtool.bumpver import bumpver

    bumpver(part, publish=publish)


@app.command
def clr_chmod():
    """Remove execute permissions from non-script files and write permissions from group/other."""
    from bhtool.clr_chmod import clr_chmod as clr_chmod_run

    clr_chmod_run()


@app.command
def npread(*files: str):
    """Print shape of numpy .npy files."""
    if not files:
        app["npread"].help_print()
        return
    from bhtool.npread import npread

    npread(files)


@app.command
def psword(*words: str, kill: bool = False):
    """Find processes by name and optionally kill them."""
    if not words:
        app["psword"].help_print()
        return
    from bhtool.psword import psword

    psword(words, kill=kill)


@app.command
def rm_npm():
    """Recursively remove node_modules directories and package-lock.json files."""
    from bhtool.rm_npm import rm_npm

    rm_npm()


@app.command
def text(in_fname: str | None = None, out_fname: str | None = None):
    """Interconvert text-based formats: md, pug, docx, html."""
    if in_fname is None or out_fname is None:
        app["text"].help_print()
        return
    from bhtool.text import convert_text

    convert_text(in_fname, out_fname)


@app.command
def todict(json: str | None = None, yaml: str | None = None):
    """Convert JSON or YAML to Python dict format."""
    from bhtool.todict import todict

    todict(json=json, yaml=yaml)


@app.command(name="movies")
def movies(root_dir: str | None = None, execute: bool = False):
    """Normalize movie directory and file names with an LLM (dry-run table by default).

    :param root_dir: Root directory containing movies (positional); default is current working directory.
    :param execute: If true, perform renames; otherwise dry run (table output).
    """
    from bhtool.list_movies import rename

    if root_dir == "rename":
        root_dir = None
    rename(root_dir=root_dir, execute=execute)


def main() -> None:
    app()
