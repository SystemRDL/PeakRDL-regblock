from ..lib.sim_testcase import SimTestCase

class Test(SimTestCase):
    incompatible_sim_tools = {"xilinx"}
    def test_dut(self):
        self.run_test()
