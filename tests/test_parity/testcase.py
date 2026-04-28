from ..lib.sim_testcase import SimTestCase

class Test(SimTestCase):
    def test_dut(self):
        self.run_test()

class TestOddParity(SimTestCase):
    odd_parity = True

    def test_dut(self):
        self.run_test()
