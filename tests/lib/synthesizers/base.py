from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..synth_testcase import SynthTestCase

class Synthesizer:
    name = ""

    @classmethod
    def is_installed(cls) -> bool:
        raise NotImplementedError

    def __init__(self, testcase: 'SynthTestCase' = None) -> None:
        self.testcase = testcase

    def run(self) -> None:
        raise NotImplementedError
