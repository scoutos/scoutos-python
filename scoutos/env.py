from __future__ import annotations

import os


def get_env(key: str, *, default_value: str | None = None) -> str:
    """Get environment variable or raise if not found"""
    value = os.environ.get(key) or default_value
    if value is None:
        message = f"No value found for {key}"
        raise KeyError(message)

    return value
