from ..base import CpuifTestMode

from peakrdl_regblock.cpuif.apb4 import APB4_Cpuif as SvAPB4_Cpuif
from peakrdl_regblock.cpuif.apb4 import APB4_Cpuif_flattened as SvAPB4_Cpuif_flattened
from peakrdl_regblock_vhdl.cpuif.apb4 import APB4_Cpuif as VhdlAPB4_Cpuif
from peakrdl_regblock_vhdl.cpuif.apb4 import APB4_Cpuif_flattened as VhdlAPB4_Cpuif_flattened

class APB4(CpuifTestMode):
    sv_cpuif_cls = SvAPB4_Cpuif
    vhdl_cpuif_cls = VhdlAPB4_Cpuif
    rtl_files = [
        "../../../hdl-src/apb4_intf.sv",
        "../../../../hdl-src/apb4_intf_pkg.vhd",
    ]
    tb_files = [
        "../../../hdl-src/apb4_intf.sv",
        "../../../../hdl-src/apb4_intf_pkg.vhd",
        "apb4_intf_driver.sv",
    ]
    tb_template = "tb_inst.sv"

    @staticmethod
    def input_signals(cpuif: SvAPB4_Cpuif) -> list[tuple[str, int]]:
        return [
            ("psel",    1),
            ("penable", 1),
            ("pwrite",  1),
            ("pprot",   3),
            ("paddr",   cpuif.addr_width),
            ("pwdata",  cpuif.data_width),
            ("pstrb",   cpuif.data_width_bytes),
        ]

    @staticmethod
    def output_signals(cpuif: SvAPB4_Cpuif) -> list[tuple[str, int]]:
        return [
            ("pready",  1),
            ("prdata",  cpuif.data_width),
            ("pslverr", 1),
        ]


class FlatAPB4(APB4):
    sv_cpuif_cls = SvAPB4_Cpuif_flattened
    vhdl_cpuif_cls = VhdlAPB4_Cpuif_flattened
    rtl_files = []
