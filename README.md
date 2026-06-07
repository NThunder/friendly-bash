# friendly-bash

A shell hook that catches `command not found` errors and uses LLM (DeepSeek) to suggest fixes.

## Quick start

```bash
pip install git+https://github.com/NThunder/friendly-bash.git
friendly-bash install
source ~/.bashrc
```

No API key needed — uses opencode free models by default.

Now when you type a wrong command, you'll get an LLM-powered suggestion.

## Using your own API key

By default, friendly-bash uses `opencode/deepseek-v4-flash-free` (free).

### Via opencode provider

Use any model from `opencode models`:

```bash
export FRIENDLY_BASH_MODEL=routerai/deepseek/deepseek-v4-flash
friendly-bash install
source ~/.bashrc
```

### Via direct API key

Set `FRIENDLY_BASH_API_KEY` — no opencode needed:

```bash
export FRIENDLY_BASH_API_KEY="sk-..."
export FRIENDLY_BASH_API_URL="https://api.openai.com/v1"  # or DeepSeek, OpenRouter, etc.
export FRIENDLY_BASH_MODEL="gpt-4o"                        # optional, default: deepseek-v4-flash-free
friendly-bash install
source ~/.bashrc
```

Supported env vars:

| Variable | Default | Description |
|----------|---------|-------------|
| `FRIENDLY_BASH_API_KEY` | — | API key (uses direct API, skips opencode) |
| `FRIENDLY_BASH_API_URL` | `https://api.deepseek.com` | API base URL |
| `FRIENDLY_BASH_MODEL` | `gpt-4o-mini` | Model name |
| `DEEPSEEK_API_KEY` | — | Fallback for DeepSeek |
| `OPENAI_API_KEY` | — | Fallback for OpenAI |

## Auto-fix on command failure

After any failed command (e.g. `conda list env` with an error), friendly-bash asks:

```
🤔 Fix failed command? (rc=1) [Y/n]
```

Press `Y` to get an LLM-suggested fix.

To disable, add to `.bashrc` before `# friendly-bash`:

```bash
export FRIENDLY_BASH_DISABLE_AUTO_FIX=1
```

```
🤔 Fix failed command? (rc=1) [Y/n]
```

Press `Y` to get an LLM-suggested fix.

## Switching back to free model

To go back to the default free model:

```bash
unset FRIENDLY_BASH_MODEL
unset FRIENDLY_BASH_API_KEY
friendly-bash install
source ~/.bashrc
```

No API key needed — uses `opencode/deepseek-v4-flash-free`.

## Commands

| Command | Description |
|---------|-------------|
| `friendly-bash install` | Install the shell hook into `.bashrc`/`.zshrc` |
| `friendly-bash uninstall` | Remove the shell hook |
| `friendly-bash suggest <cmd>` | Ask LLM what went wrong with a command |
| `friendly-bash run <description>` | Describe what you want in natural language, get a command executed |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FRIENDLY_BASH_MODEL` | `opencode/deepseek-v4-flash-free` | Model name |
| `FRIENDLY_BASH_API_KEY` | — | API key (skips opencode, uses direct API) |
| `FRIENDLY_BASH_API_URL` | `https://api.deepseek.com` | API base URL |
| `FRIENDLY_BASH_DISABLE_AUTO_FIX` | — | Set to `1` to disable auto-fix on command failure |
| `DEEPSEEK_API_KEY` | — | Fallback API key |
| `OPENAI_API_KEY` | — | Fallback API key |

## Development

```bash
git clone https://github.com/<your-username>/friendly-bash.git
cd friendly-bash
pip install -e .
```
