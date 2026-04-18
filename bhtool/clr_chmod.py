#!/usr/bin/env python3

"""Reclaim for user any files that are not shell scripts"""

from path import Path

from bhtool.utils import run

skip_directories = ["__pycache__", "node_modules", ".git"]


def clr_chmod():
    for f in Path(".").iterdir():
        if f.name.startswith("."):
            continue
        if f.is_dir():
            if f.name in skip_directories:
                continue
            run(f'chmod og-w "{f}"')
        else:
            if not f.endswith("sh") and not f.endswith("bat"):
                run(f'chmod a-x "{f}"')
            run(f'chmod og-w "{f}"')
