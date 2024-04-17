import json
from pathlib import Path

import yaml


def read_data_from_file(path: Path) -> dict:
    with Path.open(path) as f:
        contents = f.read()
        if path.suffix == ".json":
            return json.loads(contents)

        if path.suffix in [".yml", ".yaml"]:
            return yaml.safe_load(contents)

        message = f"No handler found for {path.suffix} filetype"
        raise ValueError(message)
