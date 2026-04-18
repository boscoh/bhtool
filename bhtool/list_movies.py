#!/usr/bin/env python3

import asyncio
import json
import os
import re
import sys
import textwrap

from dotenv import load_dotenv
from path import Path
from cyclopts.panel import CycloptsPanel
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from microeval.llm import get_llm_client

_pkg_root = Path(__file__).parent

load_dotenv(_pkg_root / ".env")

_MOVIES_BORDER = "cyan"
_MOVIES_TITLE = "movies"


def _movies_console() -> Console:
    return Console(highlight=False)


def _panel_lines(body: Text | str, *, title: str = _MOVIES_TITLE, border: str = _MOVIES_BORDER) -> Panel:
    return Panel(
        body,
        title=title,
        border_style=border,
        box=box.ROUNDED,
        expand=True,
        title_align="left",
    )


def _status_text(status: str) -> Text:
    if status == "would rename":
        return Text(status, style="green")
    if "not found" in status:
        return Text(status, style="red")
    return Text(status, style="yellow")


NORMALIZE_SYSTEM_PROMPT = textwrap.dedent("""
    You normalize movie and TV directory and file names for a media library.

    Rules:
    - Output the title in Title Case.
    - Keep the year as (YYYY) at the end when present; infer from the name
      if needed.
    - For TV series: preserve season markers at the end if present (e.g. S1,
      S2, S01, S02, Season 1, Season 2). Keep them at the end of the
      normalized name.
    - Strip release/quality tags: [1080p], [720p], [WEBRip], [BluRay],
      [YTS.MX], codec names, group names, etc.
    - For files: normalize only the base name (before the extension); the
      extension stays unchanged in the output.
    - Preserve the original spelling of the title; only fix casing and
      punctuation.
    - Return valid JSON only, no markdown or extra text.
""").strip()

NORMALIZE_USER_PROMPT_TEMPLATE = textwrap.dedent("""
    Convert these names to normalized form. Return a single JSON object with
    two keys:
    - "directories": list of {{"original": "<dir name>",
      "normalized": "<normalized dir name>"}}
    - "files": list of {{"original": "<filename with extension>",
      "normalized": "<normalized base name without extension>"}}

    Directory names:
    {dir_list}

    File names:
    {file_list}
""").strip()


def _parse_llm_json_object(result: dict) -> dict | None:
    text = (result.get("text") or "").strip()
    if not text:
        return None
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            data = json.loads(text[start : end + 1])
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            return None
    return None


async def normalize_names_with_llm(
    dir_names, file_names, service="openai", *, console: Console | None = None
):
    if not dir_names and not file_names:
        return {"directories": [], "files": []}

    console = console or _movies_console()
    dir_list = "\n".join(f"- {n}" for n in dir_names) or "(none)"
    file_list = "\n".join(f"- {n}" for n in file_names) or "(none)"
    user_content = NORMALIZE_USER_PROMPT_TEMPLATE.format(
        dir_list=dir_list,
        file_list=file_list,
    )
    messages = [
        {"role": "system", "content": NORMALIZE_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    try:
        async with get_llm_client(service) as client:
            llm_body = Text.assemble(
                (f"service [bold]{client.service}[/bold]  model [bold]{client.model}[/bold]\n", ""),
                ("Requesting normalized names from the LLM…", "dim"),
            )
            console.print(_panel_lines(llm_body, title="LLM", border="blue"))
            result = await client.get_completion(messages)
    except Exception as e:
        err = _movies_console(stderr=True)
        err.print(CycloptsPanel(str(e), title="Error", style="red"))
        err.print(
            CycloptsPanel(
                "Set LLM_SERVICE (openai, groq, ollama, bedrock) and the matching API key or "
                "AWS/Ollama; use bhtool/.env or your environment — see README.",
                title="Hint",
                style="yellow",
            )
        )
        sys.exit(1)
    if result.get("text", "").strip().startswith("Error:"):
        raise RuntimeError(result["text"])

    data = _parse_llm_json_object(result)
    if not data:
        raise RuntimeError("LLM response could not be parsed as JSON")
    return {"directories": data.get("directories", []), "files": data.get("files", [])}


def run_normalize_with_llm(root_dir, service="openai", *, console: Console | None = None):
    console = console or _movies_console()
    root = Path(root_dir)
    video_suffixes = {".avi", ".mkv", ".mp4", ".m4v", ".mov", ".wmv", ".webm"}
    skip_names = {
        ".DS_Store",
        "list_movies.py",
        "pyproject.toml",
        ".venv",
        ".ruff_cache",
        "__pycache__",
    }
    dir_names = []
    file_names = []
    for p in root.iterdir():
        if p.name.startswith(".") or p.name in skip_names:
            continue
        if p.is_dir():
            dir_names.append(p.name)
        elif p.suffix.lower() in video_suffixes:
            file_names.append(p.name)
    dir_names.sort()
    file_names.sort()
    scan = Text.assemble(
        ("Path ", ""),
        (str(root.realpath()), "cyan"),
        ("\n", ""),
        (str(len(dir_names)), "bold"),
        (
            f" {'directory' if len(dir_names) == 1 else 'directories'}, ",
            "",
        ),
        (str(len(file_names)), "bold"),
        (
            f" {'video file' if len(file_names) == 1 else 'video files'} · ",
            "dim",
        ),
        ("LLM_SERVICE=", "dim"),
        (service, "bold"),
    )
    console.print(_panel_lines(scan, title="Scan", border=_MOVIES_BORDER))
    return asyncio.run(
        normalize_names_with_llm(dir_names, file_names, service, console=console)
    )


def rename_movies(
    root_dir, dry_run=True, mapping=None, *, console: Console | None = None
):
    console = console or _movies_console()
    root = Path(root_dir)
    if mapping is None:
        mapping = {"directories": [], "files": []}
    dirs = mapping["directories"]
    files = mapping["files"]
    renamed_count = 0
    skipped_count = 0
    table_rows = [] if dry_run else None

    for e in dirs:
        old_name, new_name = e["original"], e["normalized"]
        if old_name == new_name:
            continue
        old_path = root / old_name
        new_path = root / new_name
        if not old_path.exists():
            skipped_count += 1
            if table_rows is not None:
                table_rows.append(("DIR", old_name, new_name, "skip (not found)"))
            continue
        if new_path.exists():
            skipped_count += 1
            if table_rows is not None:
                table_rows.append(("DIR", old_name, new_name, "skip (exists)"))
            continue
        if dry_run:
            table_rows.append(("DIR", old_name, new_name, "would rename"))
        else:
            old_path.rename(new_path)
            console.print(
                Text.assemble(
                    ("✅ DIR  ", "green"),
                    (old_name, ""),
                    (" → ", "dim"),
                    (new_name, "cyan"),
                )
            )
            renamed_count += 1

    for e in files:
        old_name, new_name = e["original"], e["normalized"]
        old_path = root / old_name
        suffix = Path(old_name).suffix
        new_path = root / (new_name + suffix)
        if old_name == new_name + suffix:
            continue
        if not old_path.exists():
            skipped_count += 1
            if table_rows is not None:
                table_rows.append(
                    ("FILE", old_name, new_name + suffix, "skip (not found)")
                )
            continue
        if new_path.exists():
            skipped_count += 1
            if table_rows is not None:
                table_rows.append(
                    ("FILE", old_name, new_name + suffix, "skip (exists)")
                )
            continue
        if dry_run:
            table_rows.append(("FILE", old_name, new_name + suffix, "would rename"))
        else:
            old_path.rename(new_path)
            console.print(
                Text.assemble(
                    ("✅ FILE ", "green"),
                    (old_name, ""),
                    (" → ", "dim"),
                    (new_name + suffix, "cyan"),
                )
            )
            renamed_count += 1

    if table_rows is not None:
        tbl = Table(show_header=True, header_style="bold cyan", border_style="dim")
        tbl.add_column("Type", style="dim", no_wrap=True)
        tbl.add_column("From")
        tbl.add_column("To")
        tbl.add_column("Status")
        for typ, old_name, new_name, status in table_rows:
            tbl.add_row(typ, old_name, new_name, _status_text(status))
        body = tbl
        if not table_rows:
            body = Text("No renames to preview (all names already match or no mappings).", style="dim")
        console.print(
            Panel(
                body,
                title="Rename (dry run)",
                border_style=_MOVIES_BORDER,
                box=box.ROUNDED,
                expand=True,
                title_align="left",
            )
        )
        summary = Text.assemble(
            (str(len(table_rows)), "bold"),
            (" item", ""),
            ("s" if len(table_rows) != 1 else "", ""),
            (" in table", "dim"),
        )
        console.print(_panel_lines(summary, title="Summary", border="dim"))
    elif not dry_run:
        done = Text.assemble(
            ("Complete: ", ""),
            (str(renamed_count), "bold green"),
            (" renamed, ", ""),
            (str(skipped_count), "bold yellow"),
            (" skipped", ""),
        )
        console.print(_panel_lines(done, title="Done", border="green"))


def _root_dir(movies_dir: str | None = None) -> Path:
    if movies_dir is not None:
        return Path(movies_dir)
    return Path.cwd()


def rename(root_dir: str | None = None, execute: bool = False):
    console = _movies_console()
    intro = Text.assemble(
        ("LLM-normalize names → ", ""),
        ("movie_mapping.json", "cyan"),
        (" → preview table\n", ""),
        ("--execute", "bold"),
        (" applies renames on disk; default is dry-run (no moves).", "dim"),
    )
    console.print(_panel_lines(intro, title=_MOVIES_TITLE, border=_MOVIES_BORDER))
    root = _root_dir(root_dir)
    svc = os.environ.get("LLM_SERVICE", "openai")
    mapping = run_normalize_with_llm(root, svc, console=console)
    mapping_path = Path.cwd() / "movie_mapping.json"
    mapping_path.write_text(json.dumps(mapping, indent=2))
    saved = Text.assemble(
        ("Wrote ", ""),
        (str(mapping_path.realpath()), "cyan"),
    )
    console.print(_panel_lines(saved, title="Mapping file", border=_MOVIES_BORDER))
    console.print()
    if execute:
        console.print(
            Panel(
                Text("Applying renames on disk.", style="bold yellow"),
                title="Execute",
                border_style="yellow",
                box=box.ROUNDED,
                expand=True,
                title_align="left",
            )
        )
        rename_movies(root, dry_run=False, mapping=mapping, console=console)
    else:
        rename_movies(root, dry_run=True, mapping=mapping, console=console)
