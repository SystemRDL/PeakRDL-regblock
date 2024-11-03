from ..base import CpuifTestMode

from peakrdl_regblock_vhdl.cpuif.passthrough import PassthroughCpuif

class Passthrough(CpuifTestMode):
    cpuif_cls = PassthroughCpuif
    rtl_files = []
    tb_files = [
        "passthrough_driver.sv",
    ]
    tb_template = "tb_inst.sv"
