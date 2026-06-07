import os
import sys
import subprocess

DEFAULT_OPENCODE_MODEL = "opencode/deepseek-v4-flash-free"


def suggest_command(failed_cmd: str, args: list[str]) -> str | None:
    prompt = (
        "You are a helpful shell assistant. "
        "The user typed a failed bash command. "
        "It could be: a keyboard layout mistake (Cyrillic->Latin), a typo, "
        "or a NATURAL LANGUAGE description (e.g. 'список conda сред' = list conda envs). "
        "If it looks like natural language, translate it to a bash command. "
        "If it's a keyboard mistake, suggest the correct Latin command. "
        "Keep explanation short (1-2 lines). "
        "If suggesting a command, put it in a ```bash code block.\n\n"
        f"Failed command: {failed_cmd}"
    )
    if args:
        prompt += f"\nArguments: {' '.join(args)}"

    has_api_key = bool(os.environ.get("FRIENDLY_BASH_API_KEY") or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY"))
    model = os.environ.get("FRIENDLY_BASH_MODEL") or os.environ.get("OPENCODE_MODEL") or DEFAULT_OPENCODE_MODEL

    if has_api_key or not model.startswith("opencode/"):
        return _suggest_via_api(prompt, model)
    else:
        return _suggest_via_opencode(prompt, model)


def _suggest_via_opencode(prompt: str, model: str) -> str | None:
    result = subprocess.run(
        ["opencode", "run", "-m", model],
        input=prompt, capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        print(f"OP: rc={result.returncode} stderr={result.stderr[:200]}", file=sys.stderr)
        return None

    text = result.stdout.strip()
    if not text:
        print(f"OP: empty stdout stderr={result.stderr[:200]}", file=sys.stderr)
    return text if text else None


def _suggest_via_api(prompt: str, model: str) -> str | None:
    from openai import OpenAI

    api_key = (
        os.environ.get("FRIENDLY_BASH_API_KEY")
        or os.environ.get("DEEPSEEK_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
    )
    base_url = os.environ.get("FRIENDLY_BASH_API_URL", "https://api.deepseek.com")

    if not api_key:
        return None

    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2000,
    )
    content = resp.choices[0].message.content
    return content.strip() if content else None
