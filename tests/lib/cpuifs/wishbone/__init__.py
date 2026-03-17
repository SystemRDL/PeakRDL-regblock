from ..base import CpuifTestMode

from peakrdl_regblock.cpuif.wishbone import Wishbone_Cpuif, Wishbone_Cpuif_flattened

class Wishbone(CpuifTestMode):
    cpuif_cls = Wishbone_Cpuif
    rtl_files = [
        "../../../../hdl-src/wishbone_intf.sv",
    ]
    tb_files = [
        "../../../../hdl-src/wishbone_intf.sv",
        "wishbone_intf_driver.sv",
    ]
    tb_template = "tb_inst.sv"

class FlatWishbone(Wishbone):
    cpuif_cls = Wishbone_Cpuif_flattened
    rtl_files = []
