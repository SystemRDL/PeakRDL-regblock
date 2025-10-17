from parameterized import parameterized_class

from ..lib.sim_testcase import SimTestCase
from ..lib.test_params import get_permutations
from ..lib.cpuifs.passthrough import Passthrough

@parameterized_class(get_permutations({
    "cpuif": [Passthrough(),],
    "generate_cpuif_err": [True,],
}))
class Test(SimTestCase):
    def test_dut(self):
        self.run_test()
