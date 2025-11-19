from parameterized import parameterized_class

from ..lib.cpuifs import ALL_CPUIF
from ..lib.sim_testcase import SimTestCase
from ..lib.test_params import get_permutation_class_name, get_permutations

PARAMS = get_permutations({
    "cpuif": ALL_CPUIF,
    "regwidth" : [8, 16, 32, 64],
})
@parameterized_class(PARAMS, class_name_func=get_permutation_class_name)
class TestFanin(SimTestCase):
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
@parameterized_class(PARAMS, class_name_func=get_permutation_class_name)
class TestRetimedFanin(TestFanin):
    retime_read_fanin = True

    def test_dut(self):
        self.run_test()
