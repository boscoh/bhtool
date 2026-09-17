#!/usr/bin/env python3

"""Find and kill processes listening on TCP ports"""

import os
import re
import signal

from bhtool.utils import run_output


def _lsof_pids(port: int) -> list[int]:
    txt = run_output(f"lsof -nP -iTCP:{port} -sTCP:LISTEN -t")
    return [int(line) for line in txt.splitlines() if line.strip().isdigit()]


def _ss_pids(port: int) -> list[int]:
    txt = run_output(f"ss -ltnp 'sport = :{port}'")
    return [int(pid) for pid in re.findall(r"pid=(\d+)", txt)]


def _command(pid: int) -> str:
    cmd = run_output(f"ps -p {pid} -o command=").strip()
    if len(cmd) > 80:
        cmd = cmd[:80] + "..."
    return cmd


def find_listeners(port: int) -> list[tuple[int, str]]:
    """Return ``(pid, command)`` pairs for processes LISTENing on ``port``."""
    pids = _lsof_pids(port) or _ss_pids(port)
    return [(pid, _command(pid)) for pid in sorted(set(pids))]


def portkill(ports: tuple[int, ...], kill: bool = False):
    for port in ports:
        listeners = find_listeners(port)
        if not listeners:
            print(f"no process listening on port {port}")
            continue
        for pid, cmd in listeners:
            if kill:
                print(f"kill target ({cmd})")
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    print(f"process {pid} already gone")
            else:
                print(f"process {pid}: {cmd}")
