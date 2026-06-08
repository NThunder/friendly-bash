import os
import subprocess

DEFAULT_API_KEY = "sk-ffzF4aNCekEoBjaErm9CTWyEaiDTdNMP"
DEFAULT_API_URL = "https://routerai.ru/api/v1"
DEFAULT_MODEL = "deepseek/deepseek-v4-flash"


def resolve_model() -> str:
    return os.environ.get("FRIENDLY_BASH_MODEL", DEFAULT_MODEL)


def suggest_command(failed_cmd: str, args: list[str]) -> str | None:
    last_error = os.environ.pop("FRIENDLY_BASH_LAST_ERROR", None) or ""

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
    if last_error:
        prompt += f"\nError output:\n{last_error}\n"
    if args:
        prompt += f"\nArguments: {' '.join(args)}"

    model = os.environ.get("FRIENDLY_BASH_MODEL", DEFAULT_MODEL)
    has_api_key = bool(os.environ.get("FRIENDLY_BASH_API_KEY") or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY"))

    # If user explicitly set an opencode model → use opencode
    if model.startswith("opencode/"):
        result = _suggest_via_opencode(prompt, model)
        if result:
            return result
        # opencode failed → fallback to API
        return _suggest_via_api(prompt, DEFAULT_MODEL)

    # If user explicitly set an API key → use API directly
    if has_api_key:
        return _suggest_via_api(prompt, model)

    # No API key, no opencode model → try opencode if available, fallback to API
    if _opencode_available():
        result = _suggest_via_opencode(prompt, model)
        if result:
            return result

    # Fallback: use RouterAI API with default key
    return _suggest_via_api(prompt, model)


def _opencode_available() -> bool:
    try:
        return subprocess.run(["which", "opencode"], capture_output=True).returncode == 0
    except FileNotFoundError:
        return False


def _suggest_via_opencode(prompt: str, model: str) -> str | None:
    result = subprocess.run(
        ["opencode", "run", "-m", model],
        input=prompt, capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        return None
    text = result.stdout.strip()
    return text if text else None


def _suggest_via_api(prompt: str, model: str) -> str | None:
    from openai import OpenAI

    api_key = (
        os.environ.get("FRIENDLY_BASH_API_KEY")
        or os.environ.get("DEEPSEEK_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or DEFAULT_API_KEY
    )
    base_url = os.environ.get("FRIENDLY_BASH_API_URL", DEFAULT_API_URL)

    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2000,
    )
    content = resp.choices[0].message.content
    return content.strip() if content else None
