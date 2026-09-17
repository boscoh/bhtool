#!/usr/bin/env python3

"""Find processes with name"""

import os
import re
import signal

from bhtool.utils import run_output


def own_pids() -> set[int]:
    """Our process and its ancestors, which must never be killed."""
    parents = {
        int(pid): int(ppid)
        for pid, ppid in re.findall(
            r"(\d+)\s+(\d+)", run_output("ps -o pid=,ppid= -ax")
        )
    }
    pids = {os.getpid()}
    pid = os.getpid()
    while pid in parents and parents[pid] > 1 and parents[pid] not in pids:
        pid = parents[pid]
        pids.add(pid)
    return pids


def psword(words: tuple[str, ...], kill: bool = False):
    killed: set[int] = set()
    skip = own_pids()
    for word in words:
        txt = run_output(f"ps aux | grep {word}")
        for line in txt.splitlines():
            tokens = line.split(None, 10)
            if len(tokens) < 11:
                continue
            cmd = tokens[10]
            if cmd.startswith("grep ") or "ps aux | grep" in cmd:
                continue
            pid = int(tokens[1])
            if pid in skip or pid in killed:
                continue
            if len(cmd) > 80:
                cmd = cmd[:80] + "..."
            if kill:
                print(f"kill target ({cmd})")
                try:
                    os.kill(pid, signal.SIGKILL)
                    killed.add(pid)
                except (ProcessLookupError, PermissionError) as err:
                    print(f"could not kill {pid}: {err}")
            else:
                print(f"process {pid}: {cmd}")
