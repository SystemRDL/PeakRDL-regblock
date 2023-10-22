import os

from parameterized import parameterized_class

from ..lib.sim_testcase import SimTestCase
from ..lib.synth_testcase import SynthTestCase
from ..lib.test_params import get_permutations
from ..lib.cpuifs import ALL_CPUIF




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
