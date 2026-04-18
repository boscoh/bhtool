# bhtool

Assorted CLI utilities that are handy in Bosco’s day-to-day work—version bumps, file conversions, process helpers, macOS shortcuts, LLM-assisted movie renaming, and other small odds and ends. **Python ≥3.13.**

### Install options


| Option                                    | Description                                                                                                         |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **`uvx bhtool …`**                       | Run from PyPI on demand (no clone). Example:`uvx bhtool --help`, `uvx bhtool run cursor`.                           |
| **`uv tool install bhtool`**              | Install**`b`** / **`bhtool`** globally from PyPI (released versions).                                               |
| **`uv sync`** then **`uv run bhtool …`** | Use the project venv from a checkout (no global install).                                                           |
| **`uv tool install .`**                   | Install**`b`** / **`bhtool`** globally from the current directory (pinned copy).                                    |
| **`uv tool install --editable .`**        | Install**`b`** / **`bhtool`** globally in **editable** mode from a checkout (code changes apply without reinstall). |

## Commands


| Command         | Description                                                                                                                                                                                                    |   |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- |
| **bumpver**     | Bump version in`pyproject.toml`, commit, push; PyPI publish is on by default (`--no-publish` to skip)                                                                                                          |   |
| **run**         | Open macOS applications by partial name (e.g.`uvx bhtool run cursor` or `b run cursor` after a local install)                                                                                                  |   |
| **clear-chmod** | Remove execute bit from non-shell files; tighten group/other write                                                                                                                                             |   |
| **npread**      | Print the shape of NumPy`.npy` files                                                                                                                                                                           |   |
| **dfplot**      | Find`**/data/results`, load parquet, plot time series, save `data_logger_results.png` and open it                                                                                                              |   |
| **psword**      | Find processes by name;`--kill` to terminate                                                                                                                                                                   |   |
| **rm-npm**      | Recursively delete`node_modules` dirs and `package-lock.json` files                                                                                                                                            |   |
| **text2**       | Convert between Markdown, HTML, DOCX, and Pug (needs`pandoc` and related tools on `PATH`)                                                                                                                      |   |
| **todict**      | JSON or YAML file, or stdin, → Python`dict(...)`-style repr on stdout                                                                                                                                         |   |
| **movies**      | `uvx bhtool movies rename` (or `b movies rename`) — ask an LLM for normalized names; writes `movie_mapping.json` in the **current working directory**; `--execute` applies renames (default is dry-run table) |   |

### Movies + LLM

`LLM_SERVICE` selects the backend (`openai`, `groq`, `ollama`, `bedrock`, …). Set it in the process environment or in **`bhtool/.env`** (loaded from the installed package directory). Model defaults come from [microeval](https://pypi.org/project/microeval/)’s config for that service.

---

## jtools

Node CLI: pug formatting, agent config copy. Usage: `jtools <subcommand>`

**Install:** `cd jtools && npm install` — dependencies only; this package is not published, so run it from that directory (or `npm link` after install).

**Run (after install):** `npx jtools <subcommand>` resolves the local `jtools` binary (same as `node_modules/.bin/jtools`). Examples: `npx jtools format-pug`, `npx jtools copy-agent`.


| Subcommand     | Description                               |
| ---------------- | ------------------------------------------- |
| **format-pug** | Format pug in`./index.html`               |
| **copy-agent** | Copy`~/.claude/CLAUDE.md` → `./AGENT.md` |
