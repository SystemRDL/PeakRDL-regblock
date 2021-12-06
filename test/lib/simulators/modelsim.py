from typing import List
import subprocess
import os

from . import Simulator

class ModelSim(Simulator):
    def compile(self) -> None:
        cmd = [
            "vlog", "-sv", "-quiet", "-l", "build.log",

            # Free version of ModelSim throws errors if generate/endgenerate
            # blocks are not used.
            # These have been made optional long ago. Modern versions of SystemVerilog do
            # not require them and I prefer not to add them.
            "-suppress", "2720",

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
