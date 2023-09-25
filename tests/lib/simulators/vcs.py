from typing import List
import subprocess
import os

from . import Simulator


class Vcs(Simulator):
    def compile(self) -> None:
        cmd = [
            "vcs", "-full64", "-sverilog", "+systemverilogext+2017", "-quiet", "-l", "build.log",

            "+incdir+%s" % os.path.join(os.path.dirname(__file__), ".."),

            "-override_timescale=1ns/1ps",

            # Log waves
            "+define+WAVES_FSDB", '+define+WAVES=\"fsdb\"',
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
            "./simv", "-quiet",
            "-cm line+cond+tgl+fsm+branch+assert", "+enable_coverage=1",
            "-l", "%s.log" % test_name,
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
