# noqa: INP001
import asyncio
from pathlib import Path

from scoutos import App


async def main() -> None:
    path = Path("./app.yaml")
    app = App.load_from_file(path)
    result = await app.run()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
