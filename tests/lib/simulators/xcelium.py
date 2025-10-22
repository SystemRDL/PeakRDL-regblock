from typing import List
import subprocess
import os
import shutil
from .base import Simulator

class Xcelium(Simulator):
    """
    Don't use the Xcelium simulator, it is unable to compile & run any testcases.

    As observed in 25.03.006:
        - Using unpacked structs with more than 2 levels of nesting in clocking blocks is not
        supported.
    """
    name = "xcelium"

    @classmethod
    def is_installed(cls) -> bool:
        return (
            shutil.which("xrun") is not None
        )

    def compile(self) -> None:
        # Compile and elaborate into a snapshot
        cmd = [
            "xrun",
            "-64bit",
            "-elaborate",
            "-sv",
            "-log build.log",
            "-timescale 10ps/1ps",
            "-ENABLE_DS_UNPS", # Allow ".*" DUT connection with unpacked structs
            "-nowarn LNDER6", # Suppress warning about the `line 2 "lib/tb_base.sv" 0 file location
            "-nowarn SPDUSD", # Suppress warning about unused include directory
            "-incdir %s" % os.path.join(os.path.dirname(__file__), "..")
        ]

        if self.gui_mode:
            cmd.append("-access +rwc")

        # Add source files
        cmd.extend(self.tb_files)

        # Run command!
        subprocess.run(cmd, check=True)


    def run(self, plusargs:List[str] = None) -> None:
        plusargs = plusargs or []

        test_name = self.testcase.request.node.name

        # Call xrun on the elaborated snapshot
        cmd = [
            "xrun",
            "-64bit",
            "-log %s.log" % test_name,
            "-r worklib.tb:sv"
        ]

        if self.gui_mode:
            cmd.append("-gui")
            cmd.append('-input "@database -open waves -into waves.shm -shm -default -event"')
            cmd.append('-input "@probe -create tb -depth all -tasks -functions -all -packed 4k \
                        -unpacked 16k -memories -dynamic -variables -database waves"')
        else:
            cmd.extend([
                "-input", "@run",
            ])

        for plusarg in plusargs:
            cmd.append("+" + plusarg)
        subprocess.run(cmd, check=True)

        self.assertSimLogPass("%s.log" % test_name)


    def assertSimLogPass(self, path: str):
        self.testcase.assertTrue(os.path.isfile(path))

        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("xmsim: *E"):
                    self.testcase.fail(line)
                elif line.startswith("xmsim: *F"):
                    self.testcase.fail(line)
