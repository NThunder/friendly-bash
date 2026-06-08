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
| `FRIENDLY_BASH_API_KEY` | built-in RouterAI key | API key (override with your own) |
| `FRIENDLY_BASH_API_URL` | `https://routerai.ru/api/v1` | API base URL |
| `FRIENDLY_BASH_MODEL` | `deepseek/deepseek-v4-flash` | Model name |
| `FRIENDLY_BASH_DISABLE_AUTO_FIX` | — | Set to `1` to disable auto-fix on errors |

## Toggle on/off

Press **Ctrl+A** — or run `fb_toggle`.

## Using your own key

```bash
export FRIENDLY_BASH_API_KEY="sk-..."
export FRIENDLY_BASH_API_URL="https://api.openai.com/v1"
export FRIENDLY_BASH_MODEL="gpt-4o"
friendly-bash install
source ~/.bashrc
```

## Development

```bash
git clone https://github.com/NThunder/friendly-bash.git
cd friendly-bash
pip install -e .
```
