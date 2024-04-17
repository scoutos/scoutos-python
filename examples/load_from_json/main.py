# noqa: INP001
import asyncio
from pathlib import Path

from scoutos import App


async def main() -> None:
    """
    This is a simple example illustrating how to use the ScoutOS SDK to run a
    simple application.

    Parameters:
    - app_input (AppInput): The input data required for the application to run.

    Returns:
    - None: This function prints the result of the application run to the console.
    """
    path = Path("./app.json")
    app = App.load_from_file(path)
    result = await app.run()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
