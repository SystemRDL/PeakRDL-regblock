from ..lib.sim_testcase import SimTestCase
from ..lib.cpuifs.passthrough import Passthrough

class Test(SimTestCase):
    cpuif = Passthrough() # test with bit strobes

    def test_dut(self):
        self.run_test()
