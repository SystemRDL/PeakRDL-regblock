from typing import List

from .base import Simulator

class StubSimulator(Simulator):
    name = "stub"

    @classmethod
    def is_installed(cls) -> bool:
        # Always available!
        return True

    def compile(self) -> None:
        pass

    def run(self, plusargs: List[str] = None) -> None:
        pass
