#!/usr/bin/env python3

"""Find processes with name"""

from bhtool.utils import run, run_output


def psword_run(words: tuple[str, ...], kill: bool = False):
    for word in words:
        txt = run_output(f"ps aux | grep {word}")
        for line in txt.splitlines():
            tokens = line.split()
            i_process = tokens[1]
            cmd = " ".join(tokens[10:])
            if len(cmd) > 80:
                cmd = cmd[:80] + "..."
            if "psword" in line:
                continue
            if kill:
                print(f"kill target ({cmd})")
                run(f"kill -9 {i_process}")
            else:
                print(f"process {i_process}: {cmd}")
