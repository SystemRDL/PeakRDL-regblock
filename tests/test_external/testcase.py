from parameterized import parameterized_class

from ..lib.sim_testcase import SimTestCase
from ..lib.test_params import get_permutations
from ..lib.cpuifs.apb4 import APB4
from ..lib.cpuifs.axi4lite import AXI4Lite
from ..lib.cpuifs.passthrough import Passthrough

TEST_PARAMS = get_permutations({
    "cpuif": [
        APB4(),
        AXI4Lite(),
        Passthrough(),
    ],
    "retime_read_fanin": [True, False],
    "retime_read_response": [True, False],
    "retime_external": [True, False],
})

@parameterized_class(TEST_PARAMS)
class Test(SimTestCase):
    extra_tb_files = [
        "../lib/external_reg.sv",
        "../lib/external_block.sv",
    ]
    init_hwif_in = False
    clocking_hwif_in = False
    timeout_clk_cycles = 30000

    def test_dut(self):
        self.run_test()
