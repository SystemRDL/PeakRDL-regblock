import os

from peakrdl_regblock.cpuif.apb3 import APB3_Cpuif
from ..lib.cpuifs.apb3 import APB3
from ..lib.base_testcase import BaseTestCase


#-------------------------------------------------------------------------------

class ClassOverride_Cpuif(APB3_Cpuif):
    @property
    def port_declaration(self) -> str:
        return "user_apb3_intf.slave s_apb"

class ClassOverride_cpuiftestmode(APB3):
    cpuif_cls = ClassOverride_Cpuif


class Test_class_override(BaseTestCase):
    cpuif = ClassOverride_cpuiftestmode()

    def test_override_success(self):
        output_file = os.path.join(self.get_run_dir(), "regblock.sv")
        with open(output_file, "r") as f:
            self.assertIn(
                "user_apb3_intf.slave s_apb",
                f.read()
            )

#-------------------------------------------------------------------------------

class TemplateOverride_Cpuif(APB3_Cpuif):
    # contains the text "USER TEMPLATE OVERRIDE"
    template_path = "user_apb3_tmpl.sv"

class TemplateOverride_cpuiftestmode(APB3):
    cpuif_cls = TemplateOverride_Cpuif


class Test_template_override(BaseTestCase):
    cpuif = TemplateOverride_cpuiftestmode()

    def test_override_success(self):
        output_file = os.path.join(self.get_run_dir(), "regblock.sv")
        with open(output_file, "r") as f:
            self.assertIn(
                "USER TEMPLATE OVERRIDE",
                f.read()
            )
