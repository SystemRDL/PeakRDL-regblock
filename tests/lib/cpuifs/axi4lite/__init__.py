from ..base import CpuifTestMode

from peakrdl_regblock.cpuif.axi4lite import AXI4Lite_Cpuif as SvAXI4Lite_Cpuif
from peakrdl_regblock.cpuif.axi4lite import AXI4Lite_Cpuif_flattened as SvAXI4Lite_Cpuif_flattened
from peakrdl_regblock_vhdl.cpuif.axi4lite import AXI4Lite_Cpuif as VhdlAXI4Lite_Cpuif
from peakrdl_regblock_vhdl.cpuif.axi4lite import AXI4Lite_Cpuif_flattened as VhdlAXI4Lite_Cpuif_flattened

class AXI4Lite(CpuifTestMode):
    sv_cpuif_cls = SvAXI4Lite_Cpuif
    vhdl_cpuif_cls = VhdlAXI4Lite_Cpuif
    rtl_files = [
        "../../../hdl-src/axi4lite_intf.sv",
        "../../../../hdl-src/axi4lite_intf_pkg.vhd",
    ]
    tb_files = [
        "../../../hdl-src/axi4lite_intf.sv",
        "../../../../hdl-src/axi4lite_intf_pkg.vhd",
        "axi4lite_intf_driver.sv",
    ]
    tb_template = "tb_inst.sv"

    @staticmethod
    def input_signals(cpuif: SvAXI4Lite_Cpuif) -> list[tuple[str, int]]:
        return [
            ("awvalid", 1),
            ("awaddr",  cpuif.addr_width),
            ("awprot",  3),
            ("wvalid",  1),
            ("wdata",   cpuif.data_width),
            ("wstrb",   cpuif.data_width_bytes),
            ("bready",  1),
            ("arvalid", 1),
            ("araddr",  cpuif.addr_width),
            ("arprot",  3),
            ("rready",  1),
        ]

    @staticmethod
    def output_signals(cpuif: SvAXI4Lite_Cpuif) -> list[tuple[str, int]]:
        return [
            ("awready", 1),
            ("wready",  1),
            ("bvalid",  1),
            ("bresp",   2),
            ("arready", 1),
            ("rvalid",  1),
            ("rdata",   cpuif.data_width),
            ("rresp",   2),
        ]


class FlatAXI4Lite(AXI4Lite):
    sv_cpuif_cls = SvAXI4Lite_Cpuif_flattened
    vhdl_cpuif_cls = VhdlAXI4Lite_Cpuif_flattened
    rtl_files = []
