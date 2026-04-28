from ..lib.sim_testcase import SimTestCase


class TestEvenBytewise(SimTestCase):
    bytewise_parity = True

    def test_dut(self):
        self.run_test()


class TestOddBytewise(SimTestCase):
    bytewise_parity = True
    odd_parity = True

    def test_dut(self):
        self.run_test()
