#!/usr/bin/env python3

"""Unified `b` CLI entrypoint."""

from typing import Literal

from cyclopts import App

from btools.run import open_apps
from btools.bumpver import bump_version
from btools.clear_chmod import clear_chmod_run
from btools.npread import npread_run
from btools.psword import psword_run
from btools.rm_npm import rm_npm_run
from btools.text2 import text2_run
from btools.todict import todict_run

app = App(name="b", help="btools utilities")


@app.command(name="run")
def run(*params: str):
    """Open macOS applications by partial name match."""
    if not params:
        app["run"].help_print()
        return
    open_apps(*params)


@app.command
def bumpver(part: Literal["major", "minor", "patch"] | None = None, *, publish: bool = True):
    """Bump version in pyproject.toml, commit, push, and optionally publish to PyPI."""
    bump_version(part, publish=publish)


@app.command
def clear_chmod():
    """Remove execute permissions from non-script files and write permissions from group/other."""
    clear_chmod_run()


@app.command
def npread(*files: str):
    """Print shape of numpy .npy files."""
    if not files:
        app["npread"].help_print()
        return
    npread_run(files)


@app.command(name="dfplot")
def dfplot_cmd():
    """Find and plot parquet files from data/results directory."""
    from btools.dfplot import dfplot_run

    dfplot_run()


@app.command
def psword(*words: str, kill: bool = False):
    """Find processes by name and optionally kill them."""
    if not words:
        app["psword"].help_print()
        return
    psword_run(words, kill=kill)


@app.command
def rm_npm():
    """Recursively remove node_modules directories and package-lock.json files."""
    rm_npm_run()


@app.command
def text2(in_fname: str, out_fname: str):
    """Interconvert text-based formats: md, pug, docx, html."""
    text2_run(in_fname, out_fname)


@app.command
def todict(json: str | None = None, yaml: str | None = None):
    """Convert JSON or YAML to Python dict format."""
    todict_run(json=json, yaml=yaml)


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
    from btools.list_movies import movies_rename_impl

    movies_rename_impl(root_dir=root_dir, execute=execute)


app.command(movies_app)


def main() -> None:
    app()
