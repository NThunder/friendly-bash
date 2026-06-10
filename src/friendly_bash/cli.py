"""CLI entry points for friendly-bash."""

import os
import sys
import subprocess
import shlex
import re
import time
from pathlib import Path

from .hook import install_hook, uninstall_hook
from .llm import suggest_command, resolve_model


def main():
    if len(sys.argv) < 2:
        print("Usage: friendly-bash <command> [args...]")
        print("Commands:")
        print("  suggest <cmd> [args...]   Suggest a fix for a failed command")
        print("  fix <cmd> [args...]       Suggest a fix and output the command to run")
        print("  config <key|url|model>    Set API key, URL, or model")
        print("  install [--shell=]        Install shell hook")
        print("  uninstall [--shell=]      Uninstall shell hook")
        print("  run <natural language>    Run a command in natural language")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "install":
        shell = _parse_shell_flag()
        install_hook(shell)

    elif cmd == "uninstall":
        shell = _parse_shell_flag()
        uninstall_hook(shell)

    elif cmd == "suggest":
        if len(sys.argv) < 3:
            print("Usage: friendly-bash suggest <failed_command> [args...]")
            sys.exit(1)
        failed_cmd = sys.argv[2]
        args = sys.argv[3:]
        t0 = time.perf_counter()
        suggestion = suggest_command(failed_cmd, args)
        elapsed = time.perf_counter() - t0
        if suggestion:
            print(f"[{elapsed:.1f}s]", file=sys.stderr)
            print(suggestion)
        else:
            sys.exit(1)

    elif cmd == "fix":
        if len(sys.argv) < 3:
            print("Usage: friendly-bash fix <failed_command> [args...]")
            sys.exit(1)
        failed_cmd = sys.argv[2]
        args = sys.argv[3:]
        t0 = time.perf_counter()
        suggestion = suggest_command(failed_cmd, args)
        elapsed = time.perf_counter() - t0
        if not suggestion:
            sys.exit(1)
        extracted = _extract_command(suggestion)
        if not extracted:
            print(f"[{elapsed:.1f}s]", file=sys.stderr)
            print(suggestion, file=sys.stderr)
            sys.exit(1)
        model = resolve_model()
        print(f"[{elapsed:.1f}s | {model}]", file=sys.stderr)
        print(suggestion, file=sys.stderr)
        print(extracted)

    elif cmd == "run":
        if len(sys.argv) < 3:
            print("Usage: friendly-bash run <natural language description>")
            sys.exit(1)
        _run_natural(" ".join(sys.argv[2:]))

    elif cmd == "config":
        _cmd_config()

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


def _extract_command(suggestion: str) -> str | None:
    blocks = re.findall(r'```(?:bash)?[ \t]*\n(.*?)```', suggestion, re.DOTALL)
    for block in blocks:
        line = block.strip().split('\n')[0]
        if line and not line.startswith('#'):
            return line
    unclosed = re.findall(r'```(?:bash)?[ \t]*\n(.+)', suggestion, re.DOTALL)
    for block in unclosed:
        line = block.strip().split('\n')[0]
        if line and not line.startswith('#'):
            return line
    return None


def _cmd_config():
    config_dir = Path.home() / ".friendly-bash"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.sh"

    # Read existing config
    current = {}
    if config_file.exists():
        for line in config_file.read_text().splitlines():
            if line.startswith("export "):
                parts = line[7:].split("=", 1)
                if len(parts) == 2:
                    key = parts[0]
                    val = parts[1].strip('"')
                    current[key] = val

    if len(sys.argv) < 3:
        print("Usage: friendly-bash config <key|url|model> <value>")
        print("  friendly-bash config key sk-...")
        print("  friendly-bash config url https://...")
        print("  friendly-bash config model gpt-4o")
        print("")
        print("Current config:")
        for k, v in current.items():
            print(f"  {k}={v}")
        sys.exit(1)

    param = sys.argv[2]
    if param not in ("key", "url", "model"):
        print(f"Unknown config: {param}. Use: key, url, model")
        sys.exit(1)

    if len(sys.argv) < 4:
        print(f"Usage: friendly-bash config {param} <value>")
        sys.exit(1)

    value = sys.argv[3]
    env_map = {"key": "FRIENDLY_BASH_API_KEY", "url": "FRIENDLY_BASH_API_URL", "model": "FRIENDLY_BASH_MODEL"}
    current[env_map[param]] = value

    with open(config_file, "w") as f:
        for key in ("FRIENDLY_BASH_API_KEY", "FRIENDLY_BASH_API_URL", "FRIENDLY_BASH_MODEL"):
            val = current.get(key)
            if val:
                f.write(f'export {key}="{val}"\n')

    print(f"Saved {param} to {config_file}")


def _parse_shell_flag() -> str:
    for arg in sys.argv[2:]:
        if arg.startswith("--shell="):
            return arg.split("=", 1)[1]
    return "auto"


def _run_natural(text: str):
    from .llm import DEFAULT_MODEL, DEFAULT_API_URL
    from openai import OpenAI

    prompt = (
        "You are a bash translator. Convert the following user request "
        "into a single bash command. Output ONLY the command, no explanations, "
        "no markdown formatting.\n\n"
        f"Request: {text}"
    )

    model = os.environ.get("FRIENDLY_BASH_MODEL", DEFAULT_MODEL)
    api_key = os.environ.get("FRIENDLY_BASH_API_KEY") or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY") or ""
    base_url = os.environ.get("FRIENDLY_BASH_API_URL", DEFAULT_API_URL)

    t0 = time.perf_counter()
    if model.startswith("opencode/") and not api_key:
        result = subprocess.run(
            ["opencode", "run", "-m", model],
            input=prompt, capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            print("opencode failed", file=sys.stderr)
            sys.exit(1)
        command = result.stdout.strip()
    else:
        client = OpenAI(api_key=api_key, base_url=base_url)
        resp = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}],
            temperature=0.1, max_tokens=1000,
        )
        command = resp.choices[0].message.content.strip() if resp.choices[0].message.content else None

    elapsed = time.perf_counter() - t0

    if not command:
        print(f"[{elapsed:.1f}s] Model failed to generate a command. Try being more specific.", file=sys.stderr)
        sys.exit(1)
    print(f"[{elapsed:.1f}s]", file=sys.stderr)
    print(f"$ {command}")
    result = subprocess.run(command, shell=True)
    sys.exit(result.returncode)
