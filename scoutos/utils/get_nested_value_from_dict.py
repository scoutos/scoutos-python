from typing import Any


def get_nested_value_from_dict(path: str, data: dict) -> Any:  # noqa: ANN401
    """Given a path expressed as a string delimited with `.`, return the value
    found at the path, or `None` if it was not found."""
    for key in path.split("."):
        try:
            data = data[key]
        except (KeyError, TypeError):  # noqa: PERF203
            return None

    return data
