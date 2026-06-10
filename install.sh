#!/usr/bin/env bash
set -e

# Install friendly-bash with all dependencies
BP=""
pip install --help 2>&1 | grep -q break-system-packages && BP="--break-system-packages"
pip install $BP -q --force-reinstall --no-build-isolation git+https://github.com/NThunder/friendly-bash.git 2>/dev/null ||
pip install $BP -q --no-build-isolation git+https://github.com/NThunder/friendly-bash.git 2>/dev/null || {
    pip install $BP -q --no-build-isolation --no-deps git+https://github.com/NThunder/friendly-bash.git
    pip install $BP -q openai 2>/dev/null || true
}

friendly-bash install

# Save API key for future sessions
mkdir -p ~/.friendly-bash
if [ -n "${FRIENDLY_BASH_API_KEY-}" ]; then
    cat > ~/.friendly-bash/config.sh << CONFIGEOF
export FRIENDLY_BASH_API_KEY="${FRIENDLY_BASH_API_KEY-}"
export FRIENDLY_BASH_API_URL="${FRIENDLY_BASH_API_URL-https://openrouter.ai/api/v1}"
export FRIENDLY_BASH_MODEL="${FRIENDLY_BASH_MODEL-openai/gpt-oss-20b:free}"
CONFIGEOF
    echo "API key saved to ~/.friendly-bash/config.sh"
fi

echo ""
echo "Done! Run: source ~/.bashrc"
echo "  (set your API key in ~/.friendly-bash/config.sh if not done yet)"
