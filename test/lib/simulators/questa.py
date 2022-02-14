from typing import List
import subprocess
import os

from . import Simulator

class Questa(Simulator):
    def compile(self) -> None:
        cmd = [
            "vlog", "-sv", "-quiet", "-l", "build.log",

            "+incdir+%s" % os.path.join(os.path.dirname(__file__), ".."),

            # Use strict LRM conformance
            "-svinputport=net",

            # all warnings are errors
            "-warning", "error",

            # Ignore noisy warning about vopt-time checking of always_comb/always_latch
            "-suppress", "2583",
        ]

        # Add source files
        cmd.extend(self.tb_files)

        # Run command!
        subprocess.run(cmd, check=True)


    def run(self, plusargs:List[str] = None) -> None:
        plusargs = plusargs or []

        test_name = self.testcase_cls_inst.request.node.name

        # call vsim
        cmd = [
            "vsim", "-quiet",
            "-voptargs=+acc",
            "-msgmode", "both",
            "-do", "set WildcardFilter [lsearch -not -all -inline $WildcardFilter Memory]",
            "-do", "log -r /*;",
            "-do", "run -all; exit;",
            "-c",
            "-l", "%s.log" % test_name,
            "-wlf", "%s.wlf" % test_name,
            "tb",
        ]
        for plusarg in plusargs:
            cmd.append("+" + plusarg)
        subprocess.run(cmd, check=True)

        self.assertSimLogPass("%s.log" % test_name)


    def assertSimLogPass(self, path: str):
        self.testcase_cls_inst.assertTrue(os.path.isfile(path))

        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("# ** Error"):
                    self.testcase_cls_inst.fail(line)
                elif line.startswith("# ** Fatal"):
                    self.testcase_cls_inst.fail(line)
