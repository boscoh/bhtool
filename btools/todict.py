#!/usr/bin/env python3

"""Convert json to python dict repr"""

import io
import sys
import typing
from json import load as json_load
from json import loads as json_loads

from path import Path
from ruyaml import YAML

indent = "  "

output = io.StringIO()


def print_out(*args, **kwargs):
    print(*args, file=output, **kwargs)


def walk_d(o, level=0, skip_first_indent=False):
    curr_space = indent * level
    if not skip_first_indent:
        print_out(curr_space, end="")
    if isinstance(o, typing.Mapping):
        print_out("dict(")
        next_space = "  " * (level + 1)
        for i, (key, value) in enumerate(o.items()):
            print_out(next_space, end="")
            print_out(f"{key}=", end="")
            if isinstance(value, typing.Mapping):
                walk_d(value, level + 1, True)
            else:
                walk_d(value, level + 1, True)
        print_out(curr_space, end="")
        if level > 0:
            print_out("),", end="")
        else:
            print_out(")", end="")
        print_out()
    elif isinstance(o, typing.List):
        print_out("[", end="")
        print_out()
        for item in o:
            walk_d(item, level + 1)
        print_out(curr_space, end="")
        print_out("],", end="")
        print_out()
    elif isinstance(o, str):
        print_out(f'"{o}",', end="")
        print_out()
    else:
        print_out(f"{o},", end="")
        print_out()


def todict_run(json: str | None = None, yaml: str | None = None):
    if json:
        incoming_json = json_loads(Path(json).read_text())
    elif yaml:
        yaml_reader = YAML(typ="safe")
        yaml_reader.default_flow_style = False
        incoming_json = yaml_reader.load(Path(yaml).read_text())
    elif not sys.stdin.isatty():
        incoming_json = json_load(sys.stdin)
    else:
        from btools.cli import app

        app["todict"].help_print()
        return
    global output
    output = io.StringIO()
    walk_d(incoming_json)
    contents = output.getvalue()
    output.close()
    print(contents)
