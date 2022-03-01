from ..base import CpuifTestMode

from peakrdl.regblock.cpuif.apb3 import APB3_Cpuif, APB3_Cpuif_flattened

class APB3(CpuifTestMode):
    cpuif_cls = APB3_Cpuif
    rtl_files = [
        "apb3_intf.sv",
    ]
    tb_files = [
        "apb3_intf.sv",
        "apb3_intf_driver.sv",
    ]
    tb_template = "tb_inst.sv"

class FlatAPB3(APB3):
    cpuif_cls = APB3_Cpuif_flattened
    rtl_files = []
