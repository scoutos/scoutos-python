from dataclasses import dataclass
from typing import Self


@dataclass
class RunResult:
    """Result returned when App is run."""

    ok: bool


class App:
    """App is the entrypoint to ScoutOS Gen-AI Powered Applications."""

    def run(self: Self) -> RunResult:
        """Run the application."""
        return RunResult(ok=True)
