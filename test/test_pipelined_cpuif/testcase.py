from parameterized import parameterized_class

from ..lib.sim_testcase import SimTestCase
from ..lib.test_params import TEST_PARAMS

@parameterized_class(TEST_PARAMS)
class Test(SimTestCase):
    def test_dut(self):
        self.run_test()
