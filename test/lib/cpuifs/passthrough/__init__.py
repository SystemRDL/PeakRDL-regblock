from ..base import CpuifTestMode

from peakrdl.regblock.cpuif.passthrough import PassthroughCpuif

class Passthrough(CpuifTestMode):
    cpuif_cls = PassthroughCpuif
    rtl_files = []
    tb_files = [
        "passthrough_driver.sv",
    ]
    tb_template = "tb_inst.sv"
