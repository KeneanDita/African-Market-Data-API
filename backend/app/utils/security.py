import hashlib
import secrets

KEY_PREFIX = "afr_live_"


def generate_api_key() -> str:
    return KEY_PREFIX + secrets.token_urlsafe(24)


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def key_prefix(api_key: str) -> str:
    """Short, non-secret identifier shown in dashboards (e.g. afr_live_Ab3d...)."""
    return api_key[: len(KEY_PREFIX) + 4] + "..."
