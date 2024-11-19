from ..base import CpuifTestMode

from peakrdl_regblock.cpuif.avalon import Avalon_Cpuif, Avalon_Cpuif_flattened

class Avalon(CpuifTestMode):
    cpuif_cls = Avalon_Cpuif
    rtl_files = [
        "../../../hdl-src/avalon_mm_intf.sv",
        "../../../../hdl-src/avalon_mm_intf_pkg.vhd",
    ]
    tb_files = [
        "../../../hdl-src/avalon_mm_intf.sv",
        "../../../../hdl-src/avalon_mm_intf_pkg.vhd",
        "avalon_mm_intf_driver.sv",
    ]
    tb_template = "tb_inst.sv"

class FlatAvalon(Avalon):
    cpuif_cls = Avalon_Cpuif_flattened
    rtl_files = []
