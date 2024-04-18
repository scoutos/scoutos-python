from __future__ import annotations

import json


def parse_json(stringified_json: str) -> dict:
    if stringified_json == "":
        return {}

    return json.loads(stringified_json)
