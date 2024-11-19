from ..base import CpuifTestMode

from peakrdl_regblock.cpuif.passthrough import PassthroughCpuif as SvPassthroughCpuif
from peakrdl_regblock_vhdl.cpuif.passthrough import PassthroughCpuif as VhdlPassthroughCpuif

class Passthrough(CpuifTestMode):
    sv_cpuif_cls = SvPassthroughCpuif
    vhdl_cpuif_cls = VhdlPassthroughCpuif
    rtl_files = []
    tb_files = [
        "passthrough_driver.sv",
    ]
    tb_template = "tb_inst.sv"

    @staticmethod
    def input_signals(cpuif: SvPassthroughCpuif) -> list[tuple[str, int]]:
        return [
            ("s_cpuif_req", 1),
            ("s_cpuif_req_is_wr", 1),
            ("s_cpuif_addr", cpuif.addr_width),
            ("s_cpuif_wr_data", cpuif.data_width),
            ("s_cpuif_wr_biten", cpuif.data_width),
        ]

    @staticmethod
    def output_signals(cpuif: SvPassthroughCpuif) -> list[tuple[str, int]]:
        return [
            ("s_cpuif_req_stall_wr", 1),
            ("s_cpuif_req_stall_rd", 1),
            ("s_cpuif_rd_ack", 1),
            ("s_cpuif_rd_err", 1),
            ("s_cpuif_rd_data", cpuif.data_width),
            ("s_cpuif_wr_ack", 1),
            ("s_cpuif_wr_err", 1),
        ]
