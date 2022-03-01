from typing import List
import subprocess
import os

import pytest

from .base_testcase import BaseTestCase

@pytest.mark.skipif(os.environ.get("SKIP_SYNTH_TESTS", False), reason="user skipped")
class SynthTestCase(BaseTestCase):

    def _get_synth_files(self) -> List[str]:
        files = []
        files.extend(self.cpuif.get_synth_files())
        files.append("regblock_pkg.sv")
        files.append("regblock.sv")

        return files


    def run_synth(self) -> None:
        script = os.path.join(
            os.path.dirname(__file__),
            "synthesis/vivado/run.tcl"
        )

        cmd = [
            "vivado", "-nojournal", "-notrace",
            "-mode", "batch",
            "-log", "out.log",
            "-source", script,
            "-tclargs"
        ]
        cmd.extend(self._get_synth_files())

        subprocess.run(cmd, check=True)
