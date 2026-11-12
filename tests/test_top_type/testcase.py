import os

from parameterized import parameterized_class

from ..lib.base_testcase import BaseTestCase
from ..lib.sim_testcase import SimTestCase
from ..lib.test_params import get_permutation_class_name, get_permutations


def assert_top_type_names(testcase: BaseTestCase, type_name: str) -> None:
    output_file = os.path.join(testcase.get_run_dir(), "regblock_pkg.sv")
    with open(output_file, "r") as f:
        content = f.read()

    testcase.assertIn(f"{type_name}__in_t", content)
    testcase.assertIn(f"{type_name}__out_t", content)
    testcase.assertNotIn("regblock__in_t", content)
    testcase.assertNotIn("regblock__out_t", content)


@parameterized_class(get_permutations({
    "reuse_hwif_typedefs": [True, False],
}), class_name_func=get_permutation_class_name)
class TestNamedSubAddrmap(BaseTestCase):
    rdl_elab_target = "my_sub"

    def test_type_names(self) -> None:
        assert_top_type_names(self, "my_sub")


class TestParameterizedSubAddrmap(BaseTestCase):
    rdl_elab_target = "my_param_sub"
    rdl_elab_params = {"WIDTH": 8}

    def test_type_names(self) -> None:
        assert_top_type_names(self, "my_param_sub")


class TestNamedSubAddrmapSim(SimTestCase):
    rdl_elab_target = "my_sub"

    def test_dut(self) -> None:
        self.run_test()
