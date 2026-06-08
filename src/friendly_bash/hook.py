"""Shell hook: registers a command_not_found_handler for bash/zsh."""

import os
import sys
import subprocess
from pathlib import Path

from .llm import suggest_command

_TOGGLE_HOOK = '''\
# friendly-bash: toggle on/off (Ctrl+A)
fb_toggle() {
    if [ -f /tmp/fb_disabled ]; then
        rm -f /tmp/fb_disabled
        echo "friendly-bash: ENABLED"
    else
        touch /tmp/fb_disabled
        echo "friendly-bash: DISABLED"
    fi
}
case "$-" in *i*) bind -x '"\C-a":"fb_toggle"' 2>/dev/null || true;; esac
'''

_CNF_HOOK = '''\
# friendly-bash: command not found handler
command_not_found_handle() {
    if [ -f /tmp/fb_disabled ]; then
        echo "$1: command not found" >&2
        return 127
    fi
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

_AUTO_FIX_HOOK = '''\
# friendly-bash: auto-fix on command failure
friendly_bash_fix_last() {
    local rc=$?
    [ -f /tmp/fb_cooldown ] && return
    [ -f /tmp/fb_disabled ] && return
    local cmd
    cmd=$(HISTTIMEFORMAT= history 1 | sed 's/^ *[0-9*]* *//')
    case "$cmd" in friendly-bash*|fb_*|history*|sleep*|source*|.*|cd*|ls*|echo*|export*|unset*|which*|type*|command*|__conda*|eval*|PS1=*) return;; esac
    if [ $rc -ne 0 ] && [ -n "$cmd" ]; then
        touch /tmp/fb_cooldown
        (sleep 2; rm -f /tmp/fb_cooldown) &
        echo "🤔 Fix failed command? (rc=$rc) [Y/n] "
        read -r
        if [[ $REPLY =~ ^[Yy]?$ ]]; then
            local error=""
            case "$cmd" in rm*|mv*|cp*|dd*|mkfs*|format*|shutdown*|reboot*|poweroff*|kill*|pkill*) ;;
                *) error=$(timeout 5 bash -c "$cmd" 2>&1 1>/dev/null || true) ;;
            esac
            local result model
            model="${FRIENDLY_BASH_MODEL:-opencode/deepseek-v4-flash-free}"
            echo "🤔 friendly-bash is thinking..."
            local t0 t1
            t0=$(date +%s)
            if [ -n "${FRIENDLY_BASH_API_KEY-}" ]; then
                model="${FRIENDLY_BASH_MODEL:-deepseek-chat}"
                result=$(FRIENDLY_BASH_LAST_ERROR="$error" friendly-bash fix "$cmd" 2>/dev/null || echo "")
            else
                local prompt="The bash command failed with exit code $rc. The user likely mistyped the command. Fix the SYNTAX, do NOT try to fix side-effect errors from the error output. Suggest the corrected command in a CODE BLOCK. Command: $cmd"
                [ -n "$error" ] && prompt="$prompt"$'\nError output (for context only):\n'"$error"
                result=$(opencode run --dir $HOME/.friendly-bash/project -m "$model" "$prompt" 2>/dev/null)
            fi
            t1=$(date +%s)
            if [ -n "$result" ]; then
                echo "[$(( t1 - t0 )) s | $model]"
                echo "$result"
                local cmd_to_run
                cmd_to_run=$(echo "$result" | sed -n '/```/{n;p;}' | head -1)
                [ -z "$cmd_to_run" ] && cmd_to_run="$result"
                if [ -n "$cmd_to_run" ]; then
                    read -r -p "Execute? [Y/n] "
                    if [[ $REPLY =~ ^[Yyн]?$ ]]; then
                        eval "$cmd_to_run"
                    fi
                fi
            fi
        fi
    fi
    true
}
if [ -z "${FRIENDLY_BASH_DISABLE_AUTO_FIX-}" ]; then
    PROMPT_COMMAND="friendly_bash_fix_last${PROMPT_COMMAND:+; $PROMPT_COMMAND}"
fi
'''

INIT_SH = _TOGGLE_HOOK + _CNF_HOOK + _AUTO_FIX_HOOK
FB_DIR = Path.home() / ".friendly-bash"
INIT_FILE = FB_DIR / "init.sh"
SOURCE_LINE = '\n[ -f ~/.friendly-bash/init.sh ] && source ~/.friendly-bash/init.sh\n'


def _ensure_dirs():
    FB_DIR.mkdir(parents=True, exist_ok=True)
    project_dir = FB_DIR / "project"
    project_dir.mkdir(parents=True, exist_ok=True)
    if not (project_dir / ".git").exists():
        subprocess.run(["git", "init", "-q", str(project_dir)], capture_output=True)


def write_init():
    _ensure_dirs()
    INIT_FILE.write_text(INIT_SH)


def install_hook(shell: str = "auto"):
    if shell == "auto":
        shell = Path(os.environ.get("SHELL", "/bin/bash")).name.removesuffix(".exe")

    rc_file = {
        "bash": Path.home() / ".bashrc",
        "zsh": Path.home() / ".zshrc",
    }.get(shell)

    if not rc_file:
        print(f"Unsupported shell: {shell}. Only bash and zsh are supported.")
        sys.exit(1)

    if SOURCE_LINE.strip() in rc_file.read_text() or "# friendly-bash" in rc_file.read_text():
        uninstall_hook(shell)
        print("Updated friendly-bash hook.")

    write_init()

    with open(rc_file, "a") as f:
        f.write(SOURCE_LINE)

    print(f"Installed friendly-bash hook in {rc_file}")
    print(f"Run `source {rc_file}` or restart your shell to activate.")


def uninstall_hook(shell: str = "auto"):
    if shell == "auto":
        shell = Path(os.environ.get("SHELL", "/bin/bash")).name.removesuffix(".exe")

    rc_file = {
        "bash": Path.home() / ".bashrc",
        "zsh": Path.home() / ".zshrc",
    }.get(shell)

    if not rc_file or not rc_file.exists():
        return

    text = rc_file.read_text()
    text = text.replace(SOURCE_LINE, "")
    text = text.strip() + "\n"
    rc_file.write_text(text)

    if INIT_FILE.exists():
        INIT_FILE.unlink()

    print(f"Uninstalled friendly-bash hook from {rc_file}")
