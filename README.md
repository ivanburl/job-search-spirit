# Job Search Spirit

A Codex / ChatGPT plugin for job search and CV workflows. Python helpers and MCP commands use the same commands on Windows, macOS, and Linux.

## Setup

Initialization uses the shared [setup skill](skills/setup/SKILL.md). After installing or updating the plugin, ask your agent: "Use the Job Search Spirit setup skill to install dependencies and check readiness." The workflow is agent-neutral and runs on request; it has no Codex onboarding registration or startup hook.

The setup skill checks for `uv` and `uvx`, guides installation if needed, then runs:

```text
uv run --script scripts/setup.py setup
```

Run this from the repository root, or use an absolute path to the installed script. uv manages compatible Python versions and isolated package environments. The CV helper and setup script declare their dependencies inline, so no global Python package installation is required for those scripts.

Setup installs browser binaries, tests PDF text extraction and rendering, initializes both MCP servers and lists their tools, and checks the existing LinkedIn session. A failed component is reported separately. Initial downloads need network access; Linux browser system libraries may require installation through the host's package manager. Setup reports browser launch failures rather than silently elevating privileges.

For later diagnostics:

```text
uv run --script scripts/setup.py doctor
```

Doctor skips explicit browser installation. uv still resolves dependencies, and LinkedIn's status command may prepare its own managed browser. Both commands print JSON and exit nonzero if any check fails or needs action.

If LinkedIn requires sign-in, run:

```text
uvx --python 3.12 mcp-server-linkedin@latest --login
```

Reconnect MCP servers or start a new chat after setup. `uvx` must be visible on the desktop client's PATH. Setup does not collect credentials or log in for you. Successful MCP discovery alone does not establish an authenticated session. Scanned CVs require host vision or a separately installed OCR engine.

The same setup skill and Python script can be reused by other agents with skill and local terminal support. Agent-specific plugin packaging is separate; this repository currently includes the Codex manifest.

## Structure

```text
.codex-plugin/plugin.json   Codex plugin metadata and component references
.mcp.json                  Portable uvx commands for Scrapling and LinkedIn
skills/setup/              Shared, agent-neutral setup workflow
skills/cv-reader/          Implemented PDF CV extraction skill
skills/                    Five other workflow placeholders
scripts/setup.py           Portable setup and diagnostic orchestration
scripts/probe_runtime.py   PDF, browser, and MCP checks
assets/                    Static assets
hooks/                     Reserved; no hooks configured
src/                       Reserved for custom server code
tests/                     Synthetic PDF and setup tests
```

The `.gitkeep` files preserve reserved directories in Git.

## CV reader

Ask the plugin to read an attached CV PDF using `cv-reader`. It extracts names, GitHub and LinkedIn links, phone numbers, email, skills, education, languages, certifications, and work experience with original bullets. Structured JSON includes page evidence and review issues.

The [skill](skills/cv-reader/SKILL.md) links its [output contract](skills/cv-reader/references/output-format.md) and [design sources](skills/cv-reader/references/sources.md). The helper collects evidence; the agent interprets it into CV fields.

```text
uv run --script skills/cv-reader/scripts/extract_pdf.py cv.pdf --output cv-evidence.json --render-dir cv-pages
```

Inline dependency metadata declares `pdfplumber` and `pypdfium2`; uv installs them into an isolated environment. See [uv script dependencies](https://docs.astral.sh/uv/guides/scripts/).

## MCP servers

Both entries in `.mcp.json` use `uvx`, with no operating-system-specific launcher or executable path:

- Scrapling uses `scrapling[ai]` and the `scrapling mcp` command. [Documentation](https://scrapling.readthedocs.io/en/latest/ai/mcp-server.html).
- LinkedIn uses `mcp-server-linkedin@latest --transport stdio`, retaining automatic updates. Login state stays in the server's user data directory. [Documentation](https://github.com/stickerdaniel/linkedin-mcp-server).

See [uv tools](https://docs.astral.sh/uv/guides/tools/) for environment management. New releases, expired sessions, and network failures can change readiness after a successful check.

## Development

Run the tests using the same command on each supported operating system:

```text
uv run --no-project --python 3.12 --with pdfplumber --with pypdfium2 --with reportlab --with Pillow python -m unittest discover -s tests -v
```

Tests cover PDF evidence collection and setup failure handling; they do not prove the agent's interpretation accuracy for arbitrary CVs. Live checks can be run with the setup command above.
