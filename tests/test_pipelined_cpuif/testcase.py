from parameterized import parameterized_class

from ..lib.cpuifs import ALL_CPUIF
from ..lib.sim_testcase import SimTestCase
from ..lib.test_params import get_permutation_class_name, get_permutations


@parameterized_class(get_permutations({
    "cpuif": ALL_CPUIF,
    "retime_read_fanin": [True, False],
    "retime_read_response": [True, False],
}), class_name_func=get_permutation_class_name)
class Test(SimTestCase):
    def test_dut(self):
        self.run_test()
