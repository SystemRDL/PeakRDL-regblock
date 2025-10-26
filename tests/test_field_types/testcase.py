# Edit test_field_types/testcase.py and change it to:
from ..lib.sim_testcase import SimTestCase
from ..lib.cpuifs import FlatAPB4  # Add this line

class Test(SimTestCase):
    cpuif = FlatAPB4()  # Add this line
    
    def test_dut(self):
        self.run_test()
