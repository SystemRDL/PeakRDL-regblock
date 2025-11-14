import os
from typing import List

import pytest

from .base_testcase import BaseTestCase
from .synthesizers import get_synthesizer_cls


class SynthTestCase(BaseTestCase):

    def _get_synth_files(self) -> List[str]:
        files = []
        files.extend(self.cpuif.get_synth_files())
        files.append("regblock_pkg.sv")
        files.append("regblock.sv")

        return files

    def setUp(self) -> None:
        name = self.request.config.getoption("--synth-tool")
        synth_cls = get_synthesizer_cls(name)
        if synth_cls is None:
            pytest.skip()
        super().setUp()

    def run_synth(self) -> None:
        name = self.request.config.getoption("--synth-tool")
        synth_cls = get_synthesizer_cls(name)
        synth = synth_cls(self, request=self.request)

        # cd into the build directory
        cwd = os.getcwd()
        os.chdir(self.get_run_dir())

        try:
            synth.run()
        finally:
            # cd back
            os.chdir(cwd)
