import hashlib
import hmac as hmac_module
from flask import current_app


def get_prefix() -> str:
    from app.models.event import EventState
    state = EventState.get()
    if state and state.flag_prefix:
        return state.flag_prefix
    return current_app.config.get('FLAG_PREFIX', 'THA')


def format_flag(inner: str) -> str:
    return f"{get_prefix()}{{{inner}}}"


def generate_dynamic_flag(team_id: int, challenge_id: int) -> str:
    """Generate a per-team dynamic flag deterministically."""
    secret = current_app.config.get('DYNAMIC_FLAG_SECRET', 'dynamic-secret-key')
    data = f"{secret}:{team_id}:{challenge_id}"
    digest = hmac_module.new(
        secret.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()[:8]
    return digest


def validate_submission(submitted: str, challenge, team_id: int) -> bool:
    """
    Returns True if the submitted string matches the challenge flag.
    Accepts both bare inner value and full PREFIX{value} format.
    """
    prefix = get_prefix()

    # Strip prefix if present
    if submitted.startswith(f"{prefix}{{") and submitted.endswith('}'):
        inner = submitted[len(prefix)+1:-1]
    else:
        inner = submitted

    if challenge.is_dynamic:
        expected = generate_dynamic_flag(team_id, challenge.id)
    else:
        expected = challenge.flag

    return hmac_module.compare_digest(inner.strip(), expected.strip())
