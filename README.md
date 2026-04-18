# bhtool

CLI utilities for version bumping, file conversion, process management, and dev workflows. Python ≥3.12.

**Install:** `uv sync` · `uv pip install -e .` · `uv tool install .` (global)

| Command         | Description                                                       |
|-----------------|-------------------------------------------------------------------|
| **bumpver**     | Bump version in pyproject.toml, commit, push, optionally publish  |
| **a**           | Open macOS apps by partial name (`a chrome`, `a cursor`)          |
| **clear_chmod** | Strip execute from non-scripts, group/other write                 |
| **npread**      | Print shape of .npy files                                         |
| **dfplot**      | Plot parquet/CSV, open figure                                     |
| **psword**      | Find processes by name; `--kill` to kill                          |
| **rm_npm**      | Recursively remove node_modules and package-lock.json             |
| **text2**       | Convert md ↔ html ↔ docx ↔ pug (pandoc)                           |
| **todict**      | JSON/YAML stdin → Python dict repr                                |

---

# jtools

Node CLI: pug formatting, agent config copy. Usage: `jtools <subcommand>`

**Install:** `cd jtools && npm install`

| Subcommand     | Description                          |
|----------------|--------------------------------------|
| **format-pug** | Format pug in ./index.html           |
| **copy-agent** | Copy ~/.claude/CLAUDE.md → ./AGENT.md |

`npx jtools format-pug` · `npx jtools copy-agent` 
