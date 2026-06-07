"""CLI entry points for friendly-bash."""

import os
import sys
import subprocess
import shlex
import re
import time

from .hook import install_hook, uninstall_hook
from .llm import suggest_command


def main():
    if len(sys.argv) < 2:
        print("Usage: friendly-bash <command> [args...]")
        print("Commands:")
        print("  suggest <cmd> [args...]   Suggest a fix for a failed command")
        print("  fix <cmd> [args...]       Suggest a fix and output the command to run")
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
        print(f"[{elapsed:.1f}s]", file=sys.stderr)
        print(suggestion, file=sys.stderr)
        print(extracted)

    elif cmd == "run":
        if len(sys.argv) < 3:
            print("Usage: friendly-bash run <natural language description>")
            sys.exit(1)
        _run_natural(" ".join(sys.argv[2:]))

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


def _parse_shell_flag() -> str:
    for arg in sys.argv[2:]:
        if arg.startswith("--shell="):
            return arg.split("=", 1)[1]
    return "auto"


def _run_natural(text: str):
    from .llm import DEFAULT_OPENCODE_MODEL

    prompt = (
        "You are a bash translator. Convert the following user request "
        "into a single bash command. Output ONLY the command, no explanations, "
        "no markdown formatting.\n\n"
        f"Request: {text}"
    )

    model = os.environ.get("FRIENDLY_BASH_MODEL") or os.environ.get("OPENCODE_MODEL") or DEFAULT_OPENCODE_MODEL

    t0 = time.perf_counter()
    if model.startswith("opencode/"):
        result = subprocess.run(
            ["opencode", "run", "-m", model],
            input=prompt, capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            print("opencode failed", file=sys.stderr)
            sys.exit(1)
        command = result.stdout.strip()
    else:
        from openai import OpenAI
        api_key = os.environ.get("FRIENDLY_BASH_API_KEY") or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("No API key set for direct API mode", file=sys.stderr)
            sys.exit(1)
        client = OpenAI(api_key=api_key, base_url=os.environ.get("FRIENDLY_BASH_API_URL", "https://api.deepseek.com"))
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
