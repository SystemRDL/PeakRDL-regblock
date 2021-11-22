from parameterized import parameterized_class

from ..lib.regblock_testcase import RegblockTestCase
from ..lib.test_params import get_permutations


PARAMS = get_permutations({
    "regwidth" : [8, 16, 32, 64],
})
@parameterized_class(PARAMS)
class TestFanin(RegblockTestCase):
    retime_read_fanin = False
    n_regs = 20
    regwidth = 32

    @classmethod
    def setUpClass(cls):
        cls.rdl_elab_params = {
            "N_REGS": cls.n_regs,
            "REGWIDTH": cls.regwidth,
        }
        super().setUpClass()

    def test_dut(self):
        self.run_test()


PARAMS = get_permutations({
    "n_regs" : [1, 4, 7, 9, 11],
    "regwidth" : [8, 16, 32, 64],
})
@parameterized_class(PARAMS)
class TestRetimedFanin(TestFanin):
    retime_read_fanin = True

    def test_dut(self):
        self.run_test()
