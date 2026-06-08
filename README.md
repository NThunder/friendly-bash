# friendly-bash

![Ubuntu](https://img.shields.io/badge/Ubuntu-tested-brightgreen)
![Windows (MinGW)](https://img.shields.io/badge/Windows%20(MinGW)-beta-yellow)
![macOS](https://img.shields.io/badge/macOS-untested-lightgrey)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A shell hook that catches **command-not-found** errors AND **run-time failures**, and uses LLM to suggest fixes.

## Quick start

```bash
curl -fsSL https://raw.githubusercontent.com/NThunder/friendly-bash/main/install.sh | bash
source ~/.bashrc
```

**After install, friendly-bash is disabled by default.**  
Press **Ctrl+A** to activate it — then try `show disk space`.

> ⚠️ **No built-in API key.** You need to get your own (free) key before using.

## Get a free API key

1. Register at [openrouter.ai/keys](https://openrouter.ai/keys) (free, via GitHub/Google)
2. Click **Create Key**, copy the key starting with `sk-or-v1-`
3. Set it up:

```bash
export FRIENDLY_BASH_API_KEY="sk-or-v1-..."
export FRIENDLY_BASH_API_URL="https://openrouter.ai/api/v1"
export FRIENDLY_BASH_MODEL="openai/gpt-oss-20b:free"
friendly-bash install
source ~/.bashrc
```

Or use any other provider (OpenAI, DeepSeek, RouterAI, etc.):

```bash
export FRIENDLY_BASH_API_KEY="sk-..."
export FRIENDLY_BASH_API_URL="https://api.openai.com/v1"
export FRIENDLY_BASH_MODEL="gpt-4o"
friendly-bash install
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
