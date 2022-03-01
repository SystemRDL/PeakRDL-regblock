from typing import TYPE_CHECKING, List

from ..forloop_generator import RDLForLoopGenerator, LoopBody

if TYPE_CHECKING:
    from ..exporter import RegblockExporter
    from systemrdl.node import RegNode

class ReadbackLoopBody(LoopBody):
    def __init__(self, dim: int, iterator: str, i_type: str) -> None:
        super().__init__(dim, iterator, i_type)
        self.n_regs = 0

    def __str__(self) -> str:
        # replace $i#sz token when stringifying
        s = super().__str__()
        token = f"${self.iterator}sz"
        s = s.replace(token, str(self.n_regs))
        return s

class ReadbackAssignmentGenerator(RDLForLoopGenerator):
    i_type = "genvar"
    loop_body_cls = ReadbackLoopBody

    def __init__(self, exp:'RegblockExporter') -> None:
        super().__init__()
        self.exp = exp

        # The readback array collects all possible readback values into a flat
        # array. The array width is equal to the CPUIF bus width. Each entry in
        # the array represents an aligned read access.
        self.current_offset = 0
        self.start_offset_stack = [] # type: List[int]
        self.dim_stack = [] # type: List[int]

    @property
    def current_offset_str(self) -> str:
        """
        Derive a string that represents the current offset being assigned.
        This consists of:
        - The current integer offset
        - multiplied index of any enclosing loop

        The integer offset from "current_offset" is static and is monotonically
        incremented as more register assignments are processed.

        The component of the offset from loops is added by multiplying the current
        loop index by the loop size.
        Since the loop's size is not known at this time, it is emitted as a
        placeholder token like: $i0sz, $i1sz, $i2sz, etc
        These tokens can be replaced once the loop body has been completed and the
        size of its contents is known.
        """
        offset_parts = []
        for i in range(self._loop_level):
            offset_parts.append(f"i{i}*$i{i}sz")
        offset_parts.append(str(self.current_offset))
        return " + ".join(offset_parts)

    def enter_Reg(self, node: 'RegNode') -> None:
        # TODO: account for smaller regs that are not aligned to the bus width
        #   - offset the field bit slice as appropriate
        #   - do not always increment the current offset
        if node.has_sw_readable:
            current_bit = 0
            rd_strb = f"({self.exp.dereferencer.get_access_strobe(node)} && !decoded_req_is_wr)"
            # Fields are sorted by ascending low bit
            for field in node.fields():
                if field.is_sw_readable:
                    # insert reserved assignment before if needed
                    if field.low != current_bit:
                        self.add_content(f"assign readback_array[{self.current_offset_str}][{field.low-1}:{current_bit}] = '0;")

                    if field.msb < field.lsb:
                        # Field gets bitswapped since it is in [low:high] orientation
                        value = f"{{<<{{{self.exp.dereferencer.get_value(field)}}}}}"
                    else:
                        value = self.exp.dereferencer.get_value(field)

                    self.add_content(f"assign readback_array[{self.current_offset_str}][{field.high}:{field.low}] = {rd_strb} ? {value} : '0;")

                    current_bit = field.high + 1

            # Insert final reserved assignment if needed
            bus_width = self.exp.cpuif.data_width
            if current_bit < bus_width:
                self.add_content(f"assign readback_array[{self.current_offset_str}][{bus_width-1}:{current_bit}] = '0;")

            self.current_offset += 1

    def push_loop(self, dim: int) -> None:
        super().push_loop(dim)
        self.start_offset_stack.append(self.current_offset)
        self.dim_stack.append(dim)

    def pop_loop(self) -> None:
        start_offset = self.start_offset_stack.pop()
        dim = self.dim_stack.pop()

        # Number of registers enclosed in this loop
        n_regs = self.current_offset - start_offset
        self.current_loop.n_regs = n_regs # type: ignore

        super().pop_loop()

        # Advance current scope's offset to account for loop's contents
        self.current_offset = start_offset + n_regs * dim
