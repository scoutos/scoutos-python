from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated

import typer

from scoutos import App
from scoutos.cli.utils import parse_json

app = typer.Typer()


@app.command()
def about() -> None:
    message = """
    This is the ScoutOS CLI designed to help interact with the ScoutOS platform.
    """
    typer.echo(message)


@app.command()
def run(
    path: Annotated[str, typer.Argument()],
    app_input: Annotated[
        str,
        typer.Option(
            ...,
            help="JSON Stringified data to be used as app run input",
        ),
    ] = "",
) -> None:
    config_file_path = Path(path)
    app = App.load_from_file(config_file_path)
    parsed_app_input = parse_json(app_input)
    result = asyncio.run(app.run(parsed_app_input))

    typer.echo(result)


if __name__ == "__main__":
    app()
