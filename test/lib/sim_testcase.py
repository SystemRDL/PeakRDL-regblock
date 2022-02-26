from typing import List
import os
import jinja2 as jj

from .sv_line_anchor import SVLineAnchor

from .simulators.questa import Questa
from .simulators import StubSimulator

from .base_testcase import BaseTestCase

SIM_CLS = Questa
if os.environ.get("STUB_SIMULATOR", False):
    SIM_CLS = StubSimulator


class SimTestCase(BaseTestCase):
    #: Abort test if it exceeds this number of clock cycles
    timeout_clk_cycles = 5000

    simulator_cls = SIM_CLS

    @classmethod
    def _generate_tb(cls):
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
            "cls": cls,
            "exporter": cls.exporter,
        }

        # template path needs to be relative to the Jinja loader root
        template_path = os.path.join(cls.get_testcase_dir(), "tb_template.sv")
        template_path = os.path.relpath(template_path, template_root_path)
        template = jj_env.get_template(template_path)

        output_path = os.path.join(cls.get_run_dir(), "tb.sv")
        stream = template.stream(context)
        stream.dump(output_path)


    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create testbench from template
        cls._generate_tb()

        simulator = cls.simulator_cls(testcase_cls=cls)

        # cd into the build directory
        cwd = os.getcwd()
        os.chdir(cls.get_run_dir())
        try:
            simulator.compile()
        finally:
            # cd back
            os.chdir(cwd)


    def run_test(self, plusargs:List[str] = None) -> None:
        simulator = self.simulator_cls(testcase_cls_inst=self)
        simulator.run(plusargs)
