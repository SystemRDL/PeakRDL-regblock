import os

from parameterized import parameterized_class
import pytest

from ..lib.sim_testcase import SimTestCase
from ..lib.synth_testcase import SynthTestCase
from ..lib.test_params import get_permutations
from ..lib.cpuifs import ALL_CPUIF
from ..lib.simulators.xilinx import Xilinx




@parameterized_class(get_permutations({
    "cpuif": ALL_CPUIF,
    "retime_read_fanin": [True, False],
    "retime_read_response": [True, False],
}))
class TestCPUIFS(SimTestCase):
    def test_dut(self):
        self.run_test()



@parameterized_class(get_permutations({
    "reuse_hwif_typedefs": [True, False],
}))
class TestTypedefs(SimTestCase):
    def test_dut(self):
        self.run_test()



@parameterized_class(get_permutations({
    "default_reset_activelow": [True, False],
    "default_reset_async": [True, False],
}))
class TestDefaultResets(SimTestCase):
    def test_dut(self):
        self.run_test()



@parameterized_class(get_permutations({
    "cpuif": ALL_CPUIF,
    "retime_read_fanin": [True, False],
    "retime_read_response": [True, False],
    "reuse_hwif_typedefs": [True, False],
}))
class TestSynth(SynthTestCase):
    def test_dut(self):
        self.run_synth()



@pytest.mark.skipif(os.environ.get("STUB_SIMULATOR", False) or os.environ.get("NO_XSIM", False), reason="user skipped")
@parameterized_class(get_permutations({
    "cpuif": ALL_CPUIF,
    "retime_read_fanin": [True, False],
    "retime_read_response": [True, False],
    "reuse_hwif_typedefs": [True, False],
}))
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
