from typing import TYPE_CHECKING

from .readback_mux_generator import ReadbackMuxGenerator, RetimedReadbackMuxGenerator, RetimedExtBlockReadbackMuxGenerator
from ..utils import clog2

if TYPE_CHECKING:
    from ..exporter import RegblockExporter, DesignState

class Readback:
    def __init__(self, exp:'RegblockExporter'):
        self.exp = exp

    @property
    def ds(self) -> 'DesignState':
        return self.exp.ds

    def get_implementation(self) -> str:
        if self.ds.retime_read_fanin:
            return self.get_2stage_implementation()
        else:
            # No retiming
            return self.get_1stage_implementation()


    def get_empty_implementation(self) -> str:
        """
        Readback implementation when there are no readable registers
        """
        context = {
            "ds": self.ds,
        }
        template = self.exp.jj_env.get_template(
            "readback/templates/empty_readback.sv"
        )
        return template.render(context)


    def get_1stage_implementation(self) -> str:
        """
        Implements readback without any retiming
        """
        gen = ReadbackMuxGenerator(self.exp)
        mux_impl = gen.get_content(self.ds.top_node)

        if not mux_impl:
            # Design has no readable registers.
            return self.get_empty_implementation()

        context = {
            "readback_mux": mux_impl,
            "cpuif": self.exp.cpuif,
            "ds": self.ds,
        }
        template = self.exp.jj_env.get_template(
            "readback/templates/readback_no_rt.sv"
        )

        return template.render(context)


    def get_2stage_implementation(self) -> str:
        """
        Implements readback that is retimed to 2 stages
        """
        # Split the decode to happen in two stages, using low address bits first
        # then high address bits.
        # Split in the middle of the "relevant" address bits - the ones that
        # actually contribute to addressing in the regblock
        unused_low_addr_bits = clog2(self.exp.cpuif.data_width_bytes)
        relevant_addr_width = self.ds.addr_width - unused_low_addr_bits
        low_addr_width = (relevant_addr_width // 2) + unused_low_addr_bits
        high_addr_width = self.ds.addr_width - low_addr_width

        mux_gen = RetimedReadbackMuxGenerator(self.exp)
        mux_impl = mux_gen.get_content(self.ds.top_node)

        if not mux_impl:
            # Design has no readable addresses.
            return self.get_empty_implementation()

        if self.ds.has_external_block:
            ext_mux_gen = RetimedExtBlockReadbackMuxGenerator(self.exp)
            ext_mux_impl = ext_mux_gen.get_content(self.ds.top_node)
        else:
            ext_mux_impl = None

        context = {
            "readback_mux": mux_impl,
            "ext_block_readback_mux": ext_mux_impl,
            "cpuif": self.exp.cpuif,
            "ds": self.ds,
            "low_addr_width": low_addr_width,
            "high_addr_width": high_addr_width,
            'get_always_ff_event': self.exp.dereferencer.get_always_ff_event,
            'get_resetsignal': self.exp.dereferencer.get_resetsignal,
        }
        template = self.exp.jj_env.get_template(
            "readback/templates/readback_with_rt.sv"
        )

        return template.render(context)
