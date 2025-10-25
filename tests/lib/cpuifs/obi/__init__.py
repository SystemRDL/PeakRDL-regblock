from ..base import CpuifTestMode

from peakrdl_regblock.cpuif.obi import OBI_Cpuif, OBI_Cpuif_flattened

class OBI(CpuifTestMode):
    cpuif_cls = OBI_Cpuif
    rtl_files = [
        "../../../../hdl-src/obi_intf.sv",
    ]
    tb_files = [
        "../../../../hdl-src/obi_intf.sv",
        "obi_intf_driver.sv",
    ]
    tb_template = "tb_inst.sv"

class FlatOBI(OBI):
    cpuif_cls = OBI_Cpuif_flattened
    rtl_files = []
