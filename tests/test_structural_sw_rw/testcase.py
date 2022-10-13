import os

from parameterized import parameterized_class

from ..lib.sim_testcase import SimTestCase
from ..lib.synth_testcase import SynthTestCase
from ..lib.test_params import TEST_PARAMS
from ..lib.simulators.xilinx import Xilinx
import pytest

@parameterized_class(TEST_PARAMS)
class Test(SimTestCase):
    def test_dut(self):
        self.run_test()

@parameterized_class(TEST_PARAMS)
class TestSynth(SynthTestCase):
    def test_dut(self):
        self.run_synth()


@pytest.mark.skipif(os.environ.get("STUB_SIMULATOR", False) or os.environ.get("NO_XSIM", False), reason="user skipped")
@parameterized_class(TEST_PARAMS)
class TestVivado(SimTestCase):
    """
    Vivado XSIM's implementation of clocking blocks is broken, which is heavily used
    by the testbench infrastructure in most testcases.
    Since this group of tests does not rely on writing HWIF values, the bugs in
    xsim are avoided.

    Run this testcase using xsim to get some cross-simulator coverage.
    Goal is to validate the generated RTL doesn't use constructs that offend xsim.

    This is skipped in CI stub tests as it doesn't add value
    """

    simulator_cls = Xilinx

    def test_dut(self):
        self.run_test()
