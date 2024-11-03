from ..base import CpuifTestMode

from peakrdl_regblock_vhdl.cpuif.apb3 import APB3_Cpuif, APB3_Cpuif_flattened

class APB3(CpuifTestMode):
    cpuif_cls = APB3_Cpuif
    rtl_files = [
        "../../../../hdl-src/apb3_intf.sv",
    ]
    tb_files = [
        "../../../../hdl-src/apb3_intf.sv",
        "apb3_intf_driver.sv",
    ]
    tb_template = "tb_inst.sv"

class FlatAPB3(APB3):
    cpuif_cls = APB3_Cpuif_flattened
    rtl_files = []
