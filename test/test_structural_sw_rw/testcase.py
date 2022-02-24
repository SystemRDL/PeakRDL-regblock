from parameterized import parameterized_class

from ..lib.sim_testcase import SimTestCase
from ..lib.synth_testcase import SynthTestCase
from ..lib.test_params import TEST_PARAMS

@parameterized_class(TEST_PARAMS)
class Test(SimTestCase):
    def test_dut(self):
        self.run_test()

@parameterized_class(TEST_PARAMS)
class TestSynth(SynthTestCase):
    def test_dut(self):
        self.run_synth()
