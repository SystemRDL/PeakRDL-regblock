from ..lib.sim_testcase import SimTestCase

class Test(SimTestCase):
    incompatible_sim_tools = {"xsim"} # due to cb struct assignment bug
    def test_dut(self):
        self.run_test()
