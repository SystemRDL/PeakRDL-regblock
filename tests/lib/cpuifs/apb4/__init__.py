from ..base import CpuifTestMode

from peakrdl_regblock.cpuif.apb4 import APB4_Cpuif, APB4_Cpuif_flattened

class APB4(CpuifTestMode):
    cpuif_cls = APB4_Cpuif
    rtl_files = [
        "../../../../hdl-src/apb4_intf.sv",
    ]
    tb_files = [
        "../../../../hdl-src/apb4_intf.sv",
        "apb4_intf_driver.sv",
    ]
    tb_template = "tb_inst.sv"

class FlatAPB4(APB4):
    cpuif_cls = APB4_Cpuif_flattened
    rtl_files = []
