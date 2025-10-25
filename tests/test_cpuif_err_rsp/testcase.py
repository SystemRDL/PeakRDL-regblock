from parameterized import parameterized_class

from ..lib.sim_testcase import SimTestCase
from ..lib.test_params import get_permutations
from ..lib.cpuifs import ALL_CPUIF

@parameterized_class(get_permutations({
    "cpuif": ALL_CPUIF,
}))
class Test(SimTestCase):
    generate_cpuif_err = True

    extra_tb_files = [
        "../lib/external_reg.sv",
        "../lib/external_block.sv",
    ]

    def test_dut(self):
        self.run_test()
