import os
import shutil
import subprocess

from .base import Synthesizer


class Vivado(Synthesizer):
    name = "vivado"

    @classmethod
    def is_installed(cls) -> bool:
        return shutil.which("vivado") is not None

    def run(self) -> None:
        script = os.path.join(
            os.path.dirname(__file__),
            "vivado_scripts/run.tcl"
        )

        cmd = [
            "vivado", "-nojournal", "-notrace",
            "-mode", "batch",
            "-log", "out.log",
            "-source", script,
            "-tclargs", self.request.config.getoption("--synth-part")
        ]
        cmd.extend(self.testcase._get_synth_files())

        subprocess.run(cmd, check=True)
