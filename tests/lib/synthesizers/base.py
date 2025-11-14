from typing import TYPE_CHECKING, List

import pytest

if TYPE_CHECKING:
    from ..synth_testcase import SynthTestCase

class Synthesizer:
    name = ""

    #: this gets auto-loaded via the _load_request autouse fixture
    request = None # type: pytest.FixtureRequest

    @pytest.fixture(autouse=True)
    def _load_request(self, request):
        self.request = request

    @classmethod
    def is_installed(cls) -> bool:
        raise NotImplementedError

    def __init__(self, testcase: 'SynthTestCase' = None,
                 request: 'pytest.FixtureRequest' = None) -> None:
        self.testcase = testcase
        self.request = request

    def run(self) -> None:
        raise NotImplementedError
