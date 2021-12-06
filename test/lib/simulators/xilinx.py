from typing import List
import subprocess
import os

from . import Simulator

class Xilinx(Simulator):
    """
    Don't bother using the Xilinx simulator... Its buggy and extraordinarily slow.
    As observed in v2021.1, clocking block assignments do not seem to actually simulate
    correctly - assignemnt statements get ignored or the values get mangled.

    Keeping this here in case someday it works better...
    """
    def compile(self) -> None:
        cmd = [
            "xvlog", "--sv"
        ]
        cmd.extend(self.tb_files)
        subprocess.run(cmd, check=True)

        cmd = [
            "xelab",
            "--timescale", "1ns/1ps",
            "--debug", "all",
            "tb",
        ]
        subprocess.run(cmd, check=True)


    def run(self, plusargs:List[str] = None) -> None:
        plusargs = plusargs or []

        test_name = self.testcase_cls_inst.request.node.name

        # call vsim
        cmd = [
            "xsim",
            "--R",
            "--log", "%s.log" % test_name,
            "tb",
        ]

        for plusarg in plusargs:
            cmd.append("--testplusarg")
            cmd.append(plusarg)
        subprocess.run(cmd, check=True)

        self.assertSimLogPass("%s.log" % test_name)


    def assertSimLogPass(self, path: str):
        self.testcase_cls_inst.assertTrue(os.path.isfile(path))

        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("Error:"):
                    self.testcase_cls_inst.fail(line)
                elif line.startswith("Fatal:"):
                    self.testcase_cls_inst.fail(line)
