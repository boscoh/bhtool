#!/usr/bin/env python3

"""Quick open applications in Darwin"""

from path import Path

from bhtool.utils import run

search_dirs = [Path("/Applications"), Path.home() / "MyApps"]


def open_apps(*params: str):
    params = list(params)
    use_app = params[0].lower()
    for search_dir in search_dirs:
        names = [p.stem.lower() for p in search_dir.glob("*")]
        if match_app := next((name for name in names if use_app in name), None):
            params[0] = match_app
            break

    params = [f'"{p}"' for p in params]
    cmd = "open -a " + " ".join(params)
    run(cmd)
