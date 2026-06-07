"""Shell hook: registers a command_not_found_handler for bash/zsh."""

import os
import sys
import subprocess
from pathlib import Path

from .llm import suggest_command

_HOOK_BODY = '''\
# friendly-bash: command not found handler
command_not_found_handle() {
    echo "🤔 friendly-bash is thinking..."
    local t0 t1 elapsed result model
    t0=$(date +%s)

    if [ -n "${FRIENDLY_BASH_API_KEY-}" ]; then
        model="${FRIENDLY_BASH_MODEL:-deepseek-chat}"
        result=$(friendly-bash fix "$@" 2>/dev/null)
    else
        model="${FRIENDLY_BASH_MODEL:-opencode/deepseek-v4-flash-free}"
        result=$(opencode run --dir $HOME/.friendly-bash/project \
            -m "$model" \
            "The user typed a failed bash command. It could be: a keyboard layout mistake (Cyrillic->Latin), a typo, or a NATURAL LANGUAGE description. If it looks like natural language (e.g. 'список conda сред' = list conda envs), translate it to a bash command. Keep explanation short. If suggesting a command, put it in CODE BLOCK. Failed: $*" \
            2>/dev/null)
    fi

    local exit_code=$?
    t1=$(date +%s)
    elapsed=$(( t1 - t0 ))
    if [ $exit_code -eq 0 ] && [ -n "$result" ]; then
        echo "[$elapsed s | $model]"
        echo "$result"
        local cmd_to_run
        cmd_to_run=$(echo "$result" | sed -n '/```/{n;p;}' | head -1)
        if [ -n "$cmd_to_run" ]; then
            read -r -p "Execute? [Y/n] "
            if [[ $REPLY =~ ^[Yyн]?$ ]]; then
                eval "$cmd_to_run"
                return $?
            fi
        fi
        return 0
    fi
    echo "[$elapsed s | $model] $1: command not found"
    return 127
}
'''

HOOK_BASH = _HOOK_BODY
HOOK_ZSH = _HOOK_BODY.replace("command_not_found_handle", "command_not_found_handler")


def _ensure_project_dir():
    project_dir = Path.home() / ".friendly-bash" / "project"
    project_dir.mkdir(parents=True, exist_ok=True)
    git_dir = project_dir / ".git"
    if not git_dir.exists():
        subprocess.run(["git", "init", "-q", str(project_dir)], capture_output=True)


def install_hook(shell: str = "auto"):
    _ensure_project_dir()

    if shell == "auto":
        shell = Path(os.environ.get("SHELL", "/bin/bash")).name

    rc_file = {
        "bash": Path.home() / ".bashrc",
        "zsh": Path.home() / ".zshrc",
    }.get(shell)

    if not rc_file:
        print(f"Unsupported shell: {shell}. Only bash and zsh are supported.")
        sys.exit(1)

    hook = HOOK_BASH if shell == "bash" else HOOK_ZSH

    if rc_file.exists() and "# friendly-bash" in rc_file.read_text():
        uninstall_hook(shell)
        print("Updated friendly-bash hook.")

    with open(rc_file, "a") as f:
        f.write("\n" + hook)

    print(f"Installed friendly-bash hook in {rc_file}")
    print(f"Run `source {rc_file}` or restart your shell to activate.")


def uninstall_hook(shell: str = "auto"):
    if shell == "auto":
        shell = Path(os.environ.get("SHELL", "/bin/bash")).name

    rc_file = {
        "bash": Path.home() / ".bashrc",
        "zsh": Path.home() / ".zshrc",
    }.get(shell)

    if not rc_file:
        return

    if not rc_file.exists():
        return

    lines = rc_file.read_text().splitlines()
    filtered = []
    skip = False
    for line in lines:
        if "# friendly-bash" in line:
            skip = True
            continue
        if skip:
            if line.strip() == "}":
                skip = False
            continue
        filtered.append(line)

    rc_file.write_text("\n".join(filtered).strip() + "\n")
    print(f"Uninstalled friendly-bash hook from {rc_file}")
