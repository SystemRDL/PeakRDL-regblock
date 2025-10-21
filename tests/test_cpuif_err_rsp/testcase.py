from parameterized import parameterized_class

from ..lib.sim_testcase import SimTestCase
from ..lib.test_params import get_permutations
from ..lib.cpuifs.passthrough import Passthrough
from ..lib.cpuifs.apb3 import APB3, FlatAPB3

@parameterized_class(get_permutations({
    "cpuif": [Passthrough(), APB3(), FlatAPB3(),],
    "generate_cpuif_err": [True,],
}))
class Test(SimTestCase):
    extra_tb_files = [
        "../lib/external_reg.sv",
        "../lib/external_block.sv",
    ]

    def test_dut(self):
        self.run_test()
