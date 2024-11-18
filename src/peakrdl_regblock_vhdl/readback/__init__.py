from typing import TYPE_CHECKING, Union
import math

from .generators import ReadbackAssignmentGenerator

if TYPE_CHECKING:
    from ..exporter import RegblockExporter, DesignState
    from systemrdl.node import AddrmapNode

class Readback:
    def __init__(self, exp:'RegblockExporter'):
        self.exp = exp
        gen = ReadbackAssignmentGenerator(self.exp)
        self.array_assignments = gen.get_content(self.top_node)
        self.array_size = gen.current_offset
        # Enabling the fanin stage doesnt make sense if readback fanin is
        # small. This also avoids pesky corner cases
        if self.array_size < 4:
            self.ds.retime_read_fanin = False

    @property
    def ds(self) -> 'DesignState':
        return self.exp.ds

    @property
    def top_node(self) -> 'AddrmapNode':
        return self.exp.ds.top_node

    @property
    def signal_declaration(self) -> str:
        cpuif = self.exp.cpuif
        declarations = []
        if self.array_assignments is not None:
            declarations.extend([
               f"signal readback_array : std_logic_vector_array1(0 to {self.array_size-1})({cpuif.data_width-1} downto 0);",
            ])
            if self.ds.retime_read_fanin:
                declarations.extend([
                   f"signal readback_array_c : std_logic_vector_array1(0 to {self.fanin_array_size-1})({cpuif.data_width-1} downto 0);",
                   f"signal readback_array_r : std_logic_vector_array1(0 to {self.fanin_array_size-1})({cpuif.data_width-1} downto 0);",
                    "signal readback_done_r : std_logic;",
                ])
        return "\n".join(declarations)

    @property
    def fanin_stride(self) -> Union[int, None]:
        """Size of fanin group to consume per fanin element, or None if read fanin is disabled"""
        if not self.ds.retime_read_fanin:
            return None

        # If adding a fanin pipeline stage, goal is to try to
        # split the fanin path in the middle so that fanin into the stage
        # and the following are roughly balanced.
        fanin_target = math.sqrt(self.array_size)

        # Size of fanin group to consume per fanin element
        fanin_stride = math.floor(fanin_target)
        return fanin_stride

    @property
    def fanin_array_size(self) -> Union[int, None]:
        """Size of readback fanin array, or None if read fanin is disabled"""
        if not self.ds.retime_read_fanin:
            return None

        # Number of array elements to reduce to.
        # Round up to an extra element in case there is some residual
        fanin_array_size = math.ceil(self.array_size / self.fanin_stride)
        return fanin_array_size


    def get_implementation(self) -> str:

        context = {
            "array_assignments" : self.array_assignments,
            "array_size" : self.array_size,
            'get_always_ff_event': self.exp.dereferencer.get_always_ff_event,
            'get_resetsignal': self.exp.dereferencer.get_resetsignal,
            "cpuif": self.exp.cpuif,
            "ds": self.ds,
        }

        if self.ds.retime_read_fanin:
            # leftovers are handled in an extra array element
            fanin_residual_stride = self.array_size % self.fanin_stride

            if fanin_residual_stride != 0:
                # If there is a partial fanin element, reduce the number of
                # loops performed in the bulk fanin stage
                fanin_loop_iter = self.fanin_array_size - 1
            else:
                fanin_loop_iter = self.fanin_array_size

            context['fanin_stride'] = self.fanin_stride
            context['fanin_array_size'] = self.fanin_array_size
            context['fanin_residual_stride'] = fanin_residual_stride
            context['fanin_loop_iter'] = fanin_loop_iter

        template = self.exp.jj_env.get_template(
            "readback/templates/readback_tmpl.vhd"
        )
        return template.render(context)
