#!/usr/bin/env python3

"""Unified bhtool CLI (`b` and `bhtool` on PATH)."""

from typing import Literal

from cyclopts import App

app = App(name="bhtool", help="bhtool utilities")


@app.command(name="run")
def run(*params: str):
    """Open macOS applications by partial name match."""
    if not params:
        app["run"].help_print()
        return
    from bhtool.run import run

    run(*params)


@app.command
def bumpver(part: Literal["major", "minor", "patch"] | None = None, *, publish: bool = True):
    """Bump version in pyproject.toml, commit, push, and optionally publish to PyPI."""
    from bhtool.bumpver import bumpver

    bumpver(part, publish=publish)


@app.command
def clear_chmod():
    """Remove execute permissions from non-script files and write permissions from group/other."""
    from bhtool.clear_chmod import clear_chmod

    clear_chmod()


@app.command
def npread(*files: str):
    """Print shape of numpy .npy files."""
    if not files:
        app["npread"].help_print()
        return
    from bhtool.npread import npread

    npread(files)


@app.command(name="dfplot")
def dfplot():
    """Find and plot parquet files from data/results directory."""
    from bhtool.dfplot import dfplot

    dfplot()


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
def text2(in_fname: str, out_fname: str):
    """Interconvert text-based formats: md, pug, docx, html."""
    from bhtool.text2 import text2

    text2(in_fname, out_fname)


@app.command
def todict(json: str | None = None, yaml: str | None = None):
    """Convert JSON or YAML to Python dict format."""
    from bhtool.todict import todict

    todict(json=json, yaml=yaml)


movies_app = App(
    name="movies",
    help="Manage movie directories and files: normalize names with LLM.",
)


@movies_app.command
def rename(root_dir: str | None = None, execute: bool = False):
    """Rename movie dirs and files to normalized names using mapping from LLM.

    :param root_dir: Root directory containing movies (positional); default is current working directory.
    :param execute: If true, perform renames; otherwise dry run (table output).
    """
    from bhtool.list_movies import rename

    rename(root_dir=root_dir, execute=execute)


app.command(movies_app)


def main() -> None:
    app()
