---
name: setup
description: Set up or diagnose Job Search Spirit dependencies, PDF extraction, browser runtimes, and LinkedIn MCP authentication on Windows, macOS, or Linux.
---

# Job Search Spirit setup

Run this shared setup workflow when the user asks to initialize, repair, or diagnose Job Search Spirit. For example: "Use the Job Search Spirit setup skill to install dependencies and check readiness." Use the host agent's available terminal tools to run the portable commands below. This skill requires no agent-specific onboarding registration.

1. Resolve the plugin root two directories above this skill folder. Check that `uv --version` and `uvx --version` work in the environment that launches MCP servers.
2. If uv is missing, use an available Python interpreter to install the `uv` package with `<python> -m pip install --user uv`, or use the official installation instructions at https://docs.astral.sh/uv/getting-started/installation/ for the host. Do not assume a shell, interpreter path, or package manager. If PATH changes are needed, explain the actual executable location and restart/reconnect requirement; installation alone does not prove the desktop client can find uvx. Respect host approvals for installation.
3. Run the same command on every platform, quoting the resolved path:

   ```text
   uv run --script "<plugin-root>/scripts/setup.py" setup
   ```

   It prepares PDF dependencies, installs browser binaries, tests PDF extraction/rendering, initializes both configured MCP servers, and checks the existing LinkedIn session. Keep uv's environments and browser caches in their standard user locations. It never rewrites shell profiles, the plugin package, or global Python packages.
4. Read each reported check, not only the exit code. A failure in one component does not imply all components failed. If Linux browser system libraries are missing, follow the Playwright error's distro-specific instructions within host permissions, then rerun setup. The script installs browser binaries; privileged system-package installation is not automatic.
5. If LinkedIn requires authentication, explain that sign-in is interactive and run the following when the user is ready to log in. Do not collect credentials in chat:

   ```text
   uvx --python 3.12 mcp-server-linkedin@latest --login
   ```

   Then rerun the diagnostic command:

   ```text
   uv run --script "<plugin-root>/scripts/setup.py" doctor
   ```

6. Reconnect the MCP servers or start a fresh chat after setup. Report verified components and any unresolved items. Never equate tool discovery with a valid LinkedIn session. Scanned CVs need host vision or a separately available OCR engine.

`doctor` runs the checks without explicitly installing browser binaries. uv still resolves the declared dependencies, and LinkedIn's own status command may prepare its managed browser. All commands require local execution; initial downloads require network access.

Sources: [uv script dependencies](https://docs.astral.sh/uv/guides/scripts/), [uv tools](https://docs.astral.sh/uv/guides/tools/).
