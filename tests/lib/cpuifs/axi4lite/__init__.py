from ..base import CpuifTestMode

from peakrdl_regblock.cpuif.axi4lite import AXI4Lite_Cpuif, AXI4Lite_Cpuif_flattened

class AXI4Lite(CpuifTestMode):
    cpuif_cls = AXI4Lite_Cpuif
    rtl_files = [
        "axi4lite_intf.sv",
    ]
    tb_files = [
        "axi4lite_intf.sv",
        "axi4lite_intf_driver.sv",
    ]
    tb_template = "tb_inst.sv"

class FlatAXI4Lite(AXI4Lite):
    cpuif_cls = AXI4Lite_Cpuif_flattened
    rtl_files = []
