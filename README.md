# friendly-bash

![Ubuntu](https://img.shields.io/badge/Ubuntu-tested-brightgreen)
![Windows (MinGW)](https://img.shields.io/badge/Windows%20(MinGW)-beta-yellow)
![macOS](https://img.shields.io/badge/macOS-untested-lightgrey)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A shell hook that catches **command-not-found** errors AND **run-time failures**, and uses LLM to suggest fixes.

## Quick start

```bash
# Install with your API key (recommended)
export FRIENDLY_BASH_API_KEY="sk-..."
curl -fsSL https://raw.githubusercontent.com/NThunder/friendly-bash/main/install.sh | bash
source ~/.bashrc
```

**The key is saved to `~/.friendly-bash/config.sh` and loaded automatically** in every new terminal. No need to set it again.

**friendly-bash starts disabled.**  
Press **Ctrl+A** to enable it (you'll see `friendly-bash: ENABLED`). Then try `show disk space`.

## Getting an API key

<details>
<summary>OpenRouter (free, with rate limits)</summary>

1. Sign up at [openrouter.ai/keys](https://openrouter.ai/keys)
2. Click **Create Key**
3. Install with your key:

```bash
export FRIENDLY_BASH_API_KEY="sk-or-v1-..."
curl -fsSL https://raw.githubusercontent.com/NThunder/friendly-bash/main/install.sh | bash
source ~/.bashrc
```

</details>

<details>
<summary>RouterAI (stable, pay-as-you-go)</summary>

```bash
export FRIENDLY_BASH_API_KEY="sk-..."
export FRIENDLY_BASH_API_URL="https://routerai.ru/api/v1"
export FRIENDLY_BASH_MODEL="deepseek/deepseek-v4-flash"
curl -fsSL https://raw.githubusercontent.com/NThunder/friendly-bash/main/install.sh | bash
source ~/.bashrc
```

</details>

**If you install without a key** — set it up later:

```bash
# View current config
friendly-bash config

# Set API key
friendly-bash config key "sk-..."
source ~/.bashrc

# Set API URL (optional, defaults to OpenRouter)
friendly-bash config url "https://openrouter.ai/api/v1"
source ~/.bashrc

# Set model (optional, defaults to gpt-oss-20b:free)
friendly-bash config model "openai/gpt-oss-20b:free"
source ~/.bashrc
```

## What it catches

| Situation | Before | After |
|-----------|--------|-------|
| Natural language | `show disk space` not found | suggests `df -h`, executes on confirm |
| Typo | `pvd` not found | suggests `pwd` |
| Wrong command syntax | `conda list envs` fails | suggests `conda env list` |

## Commands

| Command | Description |
|---------|-------------|
| `friendly-bash install` | Install shell hook |
| `friendly-bash uninstall` | Remove shell hook |
| `friendly-bash fix <cmd>` | Ask LLM for a fix |
| `friendly-bash config [key\|url\|model]` | View or change API key, URL, or model |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FRIENDLY_BASH_API_KEY` | — | Required. Get one at openrouter.ai/keys |
| `FRIENDLY_BASH_API_URL` | `https://openrouter.ai/api/v1` | API base URL |
| `FRIENDLY_BASH_MODEL` | `openai/gpt-oss-20b:free` | Model name |
| `FRIENDLY_BASH_DISABLE_AUTO_FIX` | — | Set to `1` to disable auto-fix on errors |

## Toggle on/off

Press **Ctrl+A** — or run `fb_toggle`.

## Development

```bash
git clone https://github.com/NThunder/friendly-bash.git
cd friendly-bash
pip install -e .
```
