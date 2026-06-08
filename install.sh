#!/usr/bin/env bash
set -e

# Install friendly-bash with all dependencies
BP=""
pip install --help 2>&1 | grep -q break-system-packages && BP="--break-system-packages"
pip install $BP -q --force-reinstall --no-build-isolation git+https://github.com/NThunder/friendly-bash.git 2>/dev/null ||
pip install $BP -q --no-build-isolation git+https://github.com/NThunder/friendly-bash.git 2>/dev/null || {
    # Fallback if network times out: install without deps, then add openai separately
    pip install $BP -q --no-build-isolation --no-deps git+https://github.com/NThunder/friendly-bash.git
    pip install $BP -q openai 2>/dev/null || true
}
friendly-bash install
echo ""
echo "Done! Run: source ~/.bashrc"
