# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = ["mcp", "psutil"]
# ///
"""Portable setup checks. uv owns environments; no shell or OS paths are assumed."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "scripts/probe_runtime.py"


def run(command, timeout=180, allow_failure=False, quiet=False):
    import psutil
    with psutil.Popen([str(arg) for arg in command], stdin=subprocess.DEVNULL,
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      text=True, encoding="utf-8", errors="replace") as child:
        try:
            output, errors = child.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            processes = child.children(recursive=True) + [child]
            for process in reversed(processes):
                try:
                    process.kill()
                except psutil.NoSuchProcess:
                    pass
            child.communicate()
            raise RuntimeError(f"Check timed out after {timeout}s")
        if not quiet and errors:
            print(errors[-4000:], file=sys.stderr)
        if child.returncode and not allow_failure:
            raise RuntimeError(f"Command exited with status {child.returncode}; see diagnostic output")
        return child.returncode, output


def server_commands(uv):
    config = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))
    commands = {}
    for name, entry in config["mcpServers"].items():
        if entry["command"] != "uvx":
            raise ValueError(f"Unexpected MCP launcher for {name}")
        commands[name] = [uv, "tool", "run", *entry["args"]]
    return commands


def classify_session(code, output):
    if code == 0 and "Session is valid" in output:
        return {"status": "ready"}
    return {"status": "needs_action", "detail": "LinkedIn did not confirm a valid session. Run the login command from the setup skill, then doctor. Network or browser errors may also cause this."}


def readiness(uv, install):
    commands = server_commands(uv)
    scrapling_prefix = commands["scrapling"][:-2]
    linkedin_prefix = commands["linkedin"][:-2]
    checks = {}

    def check(name, action):
        print(f"Checking {name}...", file=sys.stderr)
        try:
            action()
            checks[name] = {"status": "ready"}
        except Exception as error:
            checks[name] = {"status": "failed", "detail": str(error)}

    def cv():
        helper = ROOT / "skills/cv-reader/scripts/extract_pdf.py"
        run([uv, "run", "--script", helper, "--help"])
        run([uv, "run", "--no-project", "--python", "3.12", "--with", "pdfplumber",
             "--with", "pypdfium2", PROBE, "cv"])

    def browsers():
        if install:
            for engine in ("playwright", "patchright"):
                run([*scrapling_prefix, engine, "install", "chromium"], timeout=300)
        run([*scrapling_prefix, "python", PROBE, "browser"], timeout=90)

    check("cv", cv)
    check("scrapling_browser", browsers)
    for name, command in commands.items():
        probe_command = command + (["--no-auto-import"] if name == "linkedin" else [])
        check(name + "_mcp", lambda cmd=probe_command: run(
            [sys.executable, PROBE, "mcp", *cmd], timeout=180))
    if checks["linkedin_mcp"]["status"] == "ready":
        try:
            code, output = run([*linkedin_prefix, "--status", "--no-auto-import"],
                               timeout=240, allow_failure=True, quiet=True)
            checks["linkedin_session"] = classify_session(code, output)
        except Exception as error:
            checks["linkedin_session"] = {"status": "needs_action", "detail": str(error)}
    else:
        checks["linkedin_session"] = {"status": "not_checked"}
    return {"ready": all(item["status"] == "ready" for item in checks.values()), "checks": checks,
            "notes": ["Scanned CVs require host vision or a separately installed OCR engine.",
                      "These results describe this run, not future network or authentication availability."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("setup", "doctor"))
    args = parser.parse_args()
    uv = shutil.which("uv")
    if not uv:
        parser.exit(1, "uv is not on PATH. Run the plugin's setup skill to install it.\n")
    os.environ.setdefault("UV_HTTP_TIMEOUT", "60")
    os.environ.setdefault("PYTHONUTF8", "1")
    report = readiness(uv, install=args.mode == "setup")
    print(json.dumps(report, indent=2))
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
