from ..base import CpuifTestMode

from peakrdl_regblock.cpuif.apb3 import APB3_Cpuif as SvAPB3_Cpuif
from peakrdl_regblock.cpuif.apb3 import APB3_Cpuif_flattened as SvAPB3_Cpuif_flattened
from peakrdl_regblock_vhdl.cpuif.apb3 import APB3_Cpuif as VhdlAPB3_Cpuif
from peakrdl_regblock_vhdl.cpuif.apb3 import APB3_Cpuif_flattened as VhdlAPB3_Cpuif_flattened

class APB3(CpuifTestMode):
    sv_cpuif_cls = SvAPB3_Cpuif
    vhdl_cpuif_cls = VhdlAPB3_Cpuif
    rtl_files = [
        "../../../hdl-src/apb3_intf.sv",
        "../../../../hdl-src/apb3_intf_pkg.vhd",
    ]
    tb_files = [
        "../../../hdl-src/apb3_intf.sv",
        "../../../../hdl-src/apb3_intf_pkg.vhd",
        "apb3_intf_driver.sv",
    ]
    tb_template = "tb_inst.sv"

    @staticmethod
    def input_signals(cpuif: SvAPB3_Cpuif) -> list[tuple[str, int]]:
        return [
            ("psel",    1),
            ("penable", 1),
            ("pwrite",  1),
            ("paddr",   cpuif.addr_width),
            ("pwdata",  cpuif.data_width),
        ]

    @staticmethod
    def output_signals(cpuif: SvAPB3_Cpuif) -> list[tuple[str, int]]:
        return [
            ("pready",  1),
            ("prdata",  cpuif.data_width),
            ("pslverr", 1),
        ]

class FlatAPB3(APB3):
    sv_cpuif_cls = SvAPB3_Cpuif_flattened
    vhdl_cpuif_cls = VhdlAPB3_Cpuif_flattened
    rtl_files = []
