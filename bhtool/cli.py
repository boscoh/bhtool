#!/usr/bin/env python3

"""Unified bhtool CLI (`b` and `bhtool` on PATH)."""

from typing import Literal

from cyclopts import App

app = App(name="bhtool", help="boscoh tools")


@app.command(name="run")
def run_cmd(*params: str):
    """Open macOS applications by partial name match."""
    if not params:
        app["run"].help_print()
        return
    import bhtool.run as run_mod

    run_mod.run(*params)


@app.command(name="bumpver")
def bumpver_cmd(
    part: Literal["major", "minor", "patch"] | None = None, *, publish: bool = True
):
    """Bump version in pyproject.toml, commit, push, and optionally publish to PyPI."""
    import bhtool.bumpver as bumpver_mod

    bumpver_mod.bumpver(part, publish=publish)


@app.command(name="clr_chmod")
def clr_chmod_cmd():
    """Remove execute permissions from non-script files and write permissions from group/other."""
    import bhtool.clr_chmod as clr_chmod_mod

    clr_chmod_mod.clr_chmod()


@app.command(name="npread")
def npread_cmd(*files: str):
    """Print shape of numpy .npy files."""
    if not files:
        app["npread"].help_print()
        return
    import bhtool.npread as npread_mod

    npread_mod.npread(files)


@app.command(name="psword")
def psword_cmd(*words: str, kill: bool = False):
    """Find processes by name and optionally kill them."""
    if not words:
        app["psword"].help_print()
        return
    import bhtool.psword as psword_mod

    psword_mod.psword(words, kill=kill)


@app.command(name="rm_npm")
def rm_npm_cmd():
    """Recursively remove node_modules directories and package-lock.json files."""
    import bhtool.rm_npm as rm_npm_mod

    rm_npm_mod.rm_npm()


@app.command(name="text")
def text_cmd(in_fname: str | None = None, out_fname: str | None = None):
    """Interconvert text-based formats: md, pug, docx, html."""
    if in_fname is None or out_fname is None:
        app["text"].help_print()
        return
    import bhtool.text as text_mod

    text_mod.convert_text(in_fname, out_fname)


@app.command(name="todict")
def todict_cmd(json: str | None = None, yaml: str | None = None):
    """Convert JSON or YAML to Python dict format."""
    import bhtool.todict as todict_mod

    todict_mod.todict(json=json, yaml=yaml)


@app.command(name="movies")
def movies_cmd(root_dir: str | None = None, execute: bool = False):
    """Normalize movie directory and file names with an LLM (dry-run table by default).

    :param root_dir: Root directory containing movies (positional); default is current working directory.
    :param execute: If true, perform renames; otherwise dry run (table output).
    """
    import bhtool.list_movies as list_movies_mod

    if root_dir == "rename":
        root_dir = None
    list_movies_mod.rename(root_dir=root_dir, execute=execute)


def main() -> None:
    app()
