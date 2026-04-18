#!/usr/bin/env python3

"""Remove node_modules and package-lock.json from directories"""

from path import Path

from bhtool.utils import walk_paths


def rm_npm_run():
    print("Checking for npm modules", Path(".").resolve())

    node_modules = []
    package_locks = []
    for d in walk_paths("."):
        if d.name.endswith("node_modules"):
            node_modules.append(d)
        if d.name.endswith("package-lock.json"):
            package_locks.append(d)

    for f in reversed(package_locks):
        print("remove file", f)
        f.unlink()

    for d in reversed(node_modules):
        print("remove directory", d)
        d.rmtree()
