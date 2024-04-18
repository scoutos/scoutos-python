import typer

app = typer.Typer()


def create_greeting(name: str) -> str:
    return f"Hello, {name}!"


@app.command()
def greet(name: str = "You") -> None:
    greeting = create_greeting(name)
    print(greeting)


@app.command()
def yell(name: str = "You") -> None:
    greeting = create_greeting(name).upper()
    print(greeting)


if __name__ == "__main__":
    app()
