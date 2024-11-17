from typing import List
import subprocess
import os
import shutil

from .base import Simulator

class Questa(Simulator):
    name = "questa"

    @classmethod
    def is_installed(cls) -> bool:
        return (
            shutil.which("vlog") is not None
            and shutil.which("vcom") is not None
            and shutil.which("vsim") is not None
        )

    def compile(self) -> None:
        sv_cmd = [
            "vlog", "-sv", "-quiet", "-l", "build.log",

            "+incdir+%s" % os.path.join(os.path.dirname(__file__), ".."),

            # Use strict LRM conformance
            "-svinputport=net",

            # all warnings are errors
            "-warning", "error",

            # Ignore noisy warning about vopt-time checking of always_comb/always_latch
            "-suppress", "2583",

            # Ignore warning line number differences due to `line directive
            "-suppress", "13465",
        ]

        # Add source files
        sv_cmd.extend(self.sv_tb_files)

        # Run command!
        subprocess.run(sv_cmd, check=True)

        vhdl_cmd = [
            "vcom", "-2008", "-quiet", "-l", "build.log",

            # all warnings are errors
            "-warning", "error",
        ]

        # Add source files
        vhdl_cmd.extend(self.vhdl_tb_files)

        # Run command!
        subprocess.run(vhdl_cmd, check=True)


    def run(self, plusargs:List[str] = None) -> None:
        plusargs = plusargs or []

        test_name = self.testcase.request.node.name

        # call vsim
        cmd = [
            "vsim", "-quiet",
            "-voptargs=+acc",
            "-msgmode", "both",
            "-l", "%s.log" % test_name,
            "-wlf", "%s.wlf" % test_name,
            "tb",
            "-do", "set WildcardFilter [lsearch -not -all -inline $WildcardFilter Memory]",
            "-do", "log -r /*;",
        ]

        if self.gui_mode:
            cmd.append("-i")
        else:
            cmd.extend([
                "-do", "run -all; exit;",
                "-c",
            ])

        for plusarg in plusargs:
            cmd.append("+" + plusarg)
        subprocess.run(cmd, check=True)

        self.assertSimLogPass("%s.log" % test_name)


    def assertSimLogPass(self, path: str):
        self.testcase.assertTrue(os.path.isfile(path))

        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("# ** Error"):
                    self.testcase.fail(line)
                elif line.startswith("# ** Fatal"):
                    self.testcase.fail(line)
