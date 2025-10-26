from ..base import CpuifTestMode

from peakrdl_regblock.cpuif.ahb import AHB_Cpuif, AHB_Cpuif_flattened

class AHB(CpuifTestMode):
    cpuif_cls = AHB_Cpuif
    rtl_files = [
        "../../../../hdl-src/ahb_intf.sv",
    ]
    tb_files = [
        "../../../../hdl-src/ahb_intf.sv",
        "ahb_intf_driver.sv",
    ]
    tb_template = "tb_inst.sv"

class FlatAHB(AHB):
    cpuif_cls = AHB_Cpuif_flattened
    rtl_files = []

