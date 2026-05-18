"""
Shared utility functions.
"""
import hashlib
import secrets
import string
from typing import Optional


def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def hash_string(value: str) -> str:
    """SHA-256 hash of a string — useful for deduplication keys."""
    return hashlib.sha256(value.encode()).hexdigest()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max_length characters."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def safe_get(d: dict, *keys, default=None):
    """Safely traverse nested dicts without KeyError."""
    for key in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(key, default)
    return d
