from typing import List
import os

import jinja2 as jj
import pytest

from .sv_line_anchor import SVLineAnchor

from .simulators import get_simulator_cls

from .base_testcase import BaseTestCase


class SimTestCase(BaseTestCase):
    #: Abort test if it exceeds this number of clock cycles
    timeout_clk_cycles = 5000

    incompatible_sim_tools = set()

    tb_template_file = "tb_template.sv"

    # Paths are relative to the testcase dir
    extra_tb_files = [] # type: List[str]

    # Whether to initialize the hwif_in struct at test startup
    init_hwif_in = True

    # Control whether to include in clocking block
    clocking_hwif_in = True
    clocking_hwif_out = True

    def get_extra_tb_files(self) -> List[str]:
        paths = []
        for path in self.extra_tb_files:
            path = os.path.join(self.get_testcase_dir(), path)
            paths.append(path)
        return paths

    def _generate_tb(self):
        """
        Render the testbench template into actual tb.sv
        """
        template_root_path = os.path.join(os.path.dirname(__file__), "..")
        loader = jj.FileSystemLoader(
            template_root_path
        )
        jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined,
            extensions=[SVLineAnchor],
        )

        context = {
            "testcase": self,
            "exporter": self.sv_exporter,
        }

        # template path needs to be relative to the Jinja loader root
        template_path = os.path.join(self.get_testcase_dir(), self.tb_template_file)
        template_path = os.path.relpath(template_path, template_root_path)
        template = jj_env.get_template(template_path)

        output_path = os.path.join(self.get_run_dir(), "tb.sv")
        stream = template.stream(context)
        stream.dump(output_path)


    def setUp(self):
        name = self.request.config.getoption("--sim-tool")
        if name in self.incompatible_sim_tools:
            pytest.skip()
        simulator_cls = get_simulator_cls(name)
        if simulator_cls is None:
            pytest.skip()

        super().setUp()

        # Create testbench from template
        if not self.rerun:
            self._generate_tb()

        simulator = simulator_cls(self)

        # cd into the build directory
        cwd = os.getcwd()
        os.chdir(self.get_run_dir())
        try:
            simulator.compile()
        finally:
            # cd back
            os.chdir(cwd)


    def run_test(self, plusargs:List[str] = None) -> None:
        name = self.request.config.getoption("--sim-tool")
        simulator_cls = get_simulator_cls(name)
        simulator = simulator_cls(self)

        # cd into the build directory
        cwd = os.getcwd()
        os.chdir(self.get_run_dir())

        try:
            simulator.run(plusargs)
        finally:
            # cd back
            os.chdir(cwd)
