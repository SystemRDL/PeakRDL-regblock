from parameterized import parameterized_class

from ..lib.sim_testcase import SimTestCase
from ..lib.test_params import get_permutations

PARAMS = get_permutations({
    "n_regs" : [1, 2],
    "regwidth" : [8, 16],
    "name" : ["hello", "world"],
})
@parameterized_class(PARAMS)
class TestRetimedFanin(SimTestCase):
    n_regs = 20
    regwidth = 32
    name = "xyz"

    @classmethod
    def setUpClass(cls):
        cls.rdl_elab_params = {
            "N_REGS": cls.n_regs,
            "REGWIDTH": cls.regwidth,
            "NAME": f'"{cls.name}"',
        }
        super().setUpClass()

    def test_dut(self):
        self.run_test()
