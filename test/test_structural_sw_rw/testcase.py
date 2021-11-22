from parameterized import parameterized_class

from ..lib.regblock_testcase import RegblockTestCase
from ..lib.test_params import TEST_PARAMS

@parameterized_class(TEST_PARAMS)
class Test(RegblockTestCase):
    def test_dut(self):
        self.run_test()
