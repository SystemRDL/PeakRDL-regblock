from parameterized import parameterized_class

from ..lib.sim_testcase import SimTestCase
from ..lib.test_params import get_permutations
from ..lib.cpuifs import ALL_CPUIF

@parameterized_class(
    # To reduce the number of tests, cover all CPUIFs with both error injections enabled, and all
    # combinations of bad_addr/bad_rw with the default CPUIF only.
    get_permutations({
        "cpuif": ALL_CPUIF,
        "err_if_bad_addr": [True],
        "err_if_bad_rw": [True],
    }) +
    get_permutations({
        "err_if_bad_addr": [True, False],
        "err_if_bad_rw": [True, False],
    })
)
class Test(SimTestCase):
    extra_tb_files = [
        "../lib/external_reg.sv",
        "../lib/external_block.sv",
    ]
    init_hwif_in = False
    clocking_hwif_in = False

    def test_dut(self):
        self.run_test()
