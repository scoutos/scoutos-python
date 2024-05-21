# Scout OS

Framework for building agentic workflows

## Requirements

- Python ^3.10

## Installation

### Latest Published Version

- With [pip](https://pip.pypa.io/en/stable/): `pip install scoutos`
- With [poetry](https://python-poetry.org): `poetry add scoutos`

### Current Development Version (HEAD of `main` branch)

- With [pip](https://pip.pypa.io/en/stable/): `pip install git+https://github.com/otherwillhq/scoutos-python`
- With [poetry](https://python-poetry.org): `poetry add scoutos --git https://github.com/otherwillhq/scoutos-python`

#### Pinning to a specific commit

Given that the version currently at the HEAD of the default branch should be considered unstable, you can also pin a version to a specific SHA. You can't to this via the CLI, but you can specify a specific commit in your `pyproject.toml` as follows (making sure to replace the `rev` with your desired SHA):

```
[tool.poetry.dependencies]
scoutos = { git = "https://github.com/otherwillhq/scoutos-python.git", rev = "ab1ee13c"}
```
