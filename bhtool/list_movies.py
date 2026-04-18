#!/usr/bin/env python3

import asyncio
import json
import os
import re
import sys
import textwrap

from dotenv import load_dotenv
from path import Path
from rich.console import Console
from rich.table import Table

from microeval.llm import get_llm_client

_pkg_root = Path(__file__).parent

load_dotenv(_pkg_root / ".env")

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


async def normalize_names_with_llm(dir_names, file_names, service="openai"):
    if not dir_names and not file_names:
        return {"directories": [], "files": []}

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
            print(f"LLM: service={client.service}, model={client.model}")
            print("Getting mapping from LLM...")
            result = await client.get_completion(messages)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print(
            "No LLM client: set LLM_SERVICE (openai, groq, ollama, bedrock) and the matching "
            "API key or AWS/Ollama; use bhtool/.env or your environment — see README.",
            file=sys.stderr,
        )
        sys.exit(1)
    if result.get("text", "").strip().startswith("Error:"):
        raise RuntimeError(result["text"])

    data = _parse_llm_json_object(result)
    if not data:
        raise RuntimeError("LLM response could not be parsed as JSON")
    return {"directories": data.get("directories", []), "files": data.get("files", [])}


def run_normalize_with_llm(root_dir, service="openai"):
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
    return asyncio.run(normalize_names_with_llm(dir_names, file_names, service))


def rename_movies(root_dir, dry_run=True, mapping=None):
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
            elif dry_run:
                print(f"⚠️  SKIP: {old_name} (not found)")
            continue
        if new_path.exists():
            skipped_count += 1
            if table_rows is not None:
                table_rows.append(("DIR", old_name, new_name, "skip (exists)"))
            elif dry_run:
                print(f"⚠️  SKIP: {old_name} → {new_name} (target exists)")
            continue
        if dry_run:
            if table_rows is not None:
                table_rows.append(("DIR", old_name, new_name, "would rename"))
            else:
                print(f"📁 WOULD RENAME: {old_name}")
                print(f"            TO: {new_name}")
        else:
            old_path.rename(new_path)
            print(f"✅ RENAMED: {old_name}")
            print(f"        TO: {new_name}")
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
            elif dry_run:
                print(f"⚠️  SKIP: {old_name} (not found)")
            continue
        if new_path.exists():
            skipped_count += 1
            if table_rows is not None:
                table_rows.append(
                    ("FILE", old_name, new_name + suffix, "skip (exists)")
                )
            elif dry_run:
                print(f"⚠️  SKIP: {old_name} → {new_name}{suffix} (target exists)")
            continue
        if dry_run:
            if table_rows is not None:
                table_rows.append(("FILE", old_name, new_name + suffix, "would rename"))
            else:
                print(f"📄 WOULD RENAME: {old_name}")
                print(f"            TO: {new_name}{suffix}")
        else:
            old_path.rename(new_path)
            print(f"✅ RENAMED: {old_name}")
            print(f"        TO: {new_name}{suffix}")
            renamed_count += 1

    if table_rows is not None:
        console = Console()
        tbl = Table(title="Rename (dry run)", show_header=True, header_style="bold")
        tbl.add_column("Type", style="dim")
        tbl.add_column("From")
        tbl.add_column("To")
        tbl.add_column("Status")
        for row in table_rows:
            tbl.add_row(*row)
        console.print(tbl)
        console.print(f"\n[dim]{len(table_rows)} items[/dim]")
    elif not dry_run:
        print("\n" + "=" * 80)
        print(f"COMPLETE: {renamed_count} items renamed, {skipped_count} skipped")
        print("=" * 80)


def _root_dir(movies_dir: str | None = None) -> Path:
    if movies_dir is not None:
        return Path(movies_dir)
    return Path.cwd()


def rename(root_dir: str | None = None, execute: bool = False):
    print("Movies: LLM-normalize names here -> movie_mapping.json -> preview table.")
    print("--execute applies renames; default is dry-run (no moves).")
    root = _root_dir(root_dir)
    svc = os.environ.get("LLM_SERVICE", "openai")
    mapping = run_normalize_with_llm(root, svc)
    mapping_path = Path.cwd() / "movie_mapping.json"
    mapping_path.write_text(json.dumps(mapping, indent=2))
    print(f"Saved to {mapping_path}\n")
    if execute:
        print("⚠️  PERFORMING ACTUAL RENAME")
        rename_movies(root, dry_run=False, mapping=mapping)
    else:
        rename_movies(root, dry_run=True, mapping=mapping)
