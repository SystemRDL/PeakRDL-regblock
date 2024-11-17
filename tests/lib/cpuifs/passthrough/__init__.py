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

    sv_signal_prefix = "s_cpuif_"
    vhdl_in_signal_prefix = "s_cpuif_"
    vhdl_out_signal_prefix = "s_cpuif_"

    @staticmethod
    def input_signals(cpuif: SvPassthroughCpuif) -> list[tuple[str, int]]:
        return [
            ("req", 1),
            ("req_is_wr", 1),
            ("addr", cpuif.addr_width),
            ("wr_data", cpuif.data_width),
            ("wr_biten", cpuif.data_width),
        ]

    @staticmethod
    def output_signals(cpuif: SvPassthroughCpuif) -> list[tuple[str, int]]:
        return [
            ("req_stall_wr", 1),
            ("req_stall_rd", 1),
            ("rd_ack", 1),
            ("rd_err", 1),
            ("rd_data", cpuif.data_width),
            ("wr_ack", 1),
            ("wr_err", 1),
        ]
