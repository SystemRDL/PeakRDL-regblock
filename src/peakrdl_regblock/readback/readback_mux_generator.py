from typing import TYPE_CHECKING, List, Sequence, Optional

from systemrdl.node import RegNode, AddressableNode, FieldNode
from systemrdl.walker import WalkerAction

from ..forloop_generator import RDLForLoopGenerator
from ..utils import SVInt, do_bitswap, do_slice

if TYPE_CHECKING:
    from ..exporter import DesignState, RegblockExporter

class ReadbackMuxGenerator(RDLForLoopGenerator):
    def __init__(self, exp: 'RegblockExporter') -> None:
        super().__init__()

        self.exp = exp

        # List of address strides for each dimension
        self._array_stride_stack: List[int] = []

    @property
    def ds(self) -> 'DesignState':
        return self.exp.ds


    def enter_AddressableComponent(self, node: AddressableNode) -> Optional[WalkerAction]:
        super().enter_AddressableComponent(node)

        if node.array_dimensions:
            assert node.array_stride is not None
            # Collect strides for each array dimension
            current_stride = node.array_stride
            strides = []
            for dim in reversed(node.array_dimensions):
                strides.append(current_stride)
                current_stride *= dim
            strides.reverse()
            self._array_stride_stack.extend(strides)

        if node.external and not isinstance(node, RegNode):
            # Is an external block
            self.process_external_block(node)
            return WalkerAction.SkipDescendants

        return WalkerAction.Continue


    def process_external_block(self, node: AddressableNode) -> None:
        addr_lo = self._get_address_str(node)
        addr_hi = f"{addr_lo} + {SVInt(node.size - 1, self.exp.ds.addr_width)}"
        self.add_content(f"if((rd_mux_addr >= {addr_lo}) && (rd_mux_addr <= {addr_hi})) begin")
        data = self.exp.hwif.get_external_rd_data(node)
        self.add_content(f"    readback_data_var = {data};")
        self.add_content("end")


    def enter_Reg(self, node: RegNode) -> WalkerAction:
        fields = node.fields(sw_readable_only=True)
        if not fields:
            # Reg has no readable fields
            return WalkerAction.SkipDescendants

        if node.external:
            self.process_external_reg(node)
            return WalkerAction.SkipDescendants

        accesswidth = node.get_property('accesswidth')
        regwidth = node.get_property('regwidth')
        rbuf = node.get_property('buffer_reads')

        if rbuf:
            trigger = node.get_property('rbuffer_trigger')
            is_own_trigger = (isinstance(trigger, RegNode) and trigger == node)
            if is_own_trigger:
                if accesswidth < regwidth:
                    self.process_wide_buffered_reg_with_bypass(node, fields, regwidth, accesswidth)
                else:
                    # bypass cancels out. Behaves like a normal reg
                    self.process_reg(node, fields)
            else:
                self.process_buffered_reg(node, regwidth, accesswidth)
        elif accesswidth < regwidth:
            self.process_wide_reg(node, fields, regwidth, accesswidth)
        else:
            self.process_reg(node, fields)

        return WalkerAction.SkipDescendants


    def _get_address_str(self, node: AddressableNode, subword_offset: int=0) -> str:
        expr_width = self.ds.addr_width
        a = str(SVInt(
            node.raw_absolute_address - self.ds.top_node.raw_absolute_address + subword_offset,
            expr_width
        ))
        for i, stride in enumerate(self._array_stride_stack):
            a += f" + ({expr_width})'(i{i}) * {SVInt(stride, expr_width)}"
        return a


    def get_addr_compare_conditional(self, addr: str) -> str:
        return f"rd_mux_addr == {addr}"

    def get_readback_data_var(self, addr: str) -> str:
        return "readback_data_var"

    def process_external_reg(self, node: RegNode) -> None:
        accesswidth = node.get_property('accesswidth')
        regwidth = node.get_property('regwidth')
        data = self.exp.hwif.get_external_rd_data(node)

        if regwidth > accesswidth:
            # Is wide reg.
            # The retiming scheme requires singular address comparisons rather than
            # ranges. To support this, unroll the subwords
            n_subwords = regwidth // accesswidth
            subword_stride = accesswidth // 8
            for subword_idx in range(n_subwords):
                addr = self._get_address_str(node, subword_offset=subword_idx*subword_stride)
                conditional = self.get_addr_compare_conditional(addr)
                var = self.get_readback_data_var(addr)
                self.add_content(f"if({conditional}) begin")
                self.add_content(f"    {var} = {data};")
                self.add_content("end")
        else:
            addr = self._get_address_str(node)
            conditional = self.get_addr_compare_conditional(addr)
            var = self.get_readback_data_var(addr)
            self.add_content(f"if({conditional}) begin")
            if regwidth < self.exp.cpuif.data_width:
                self.add_content(f"    {var}[{regwidth-1}:0] = {data};")
            else:
                self.add_content(f"    {var} = {data};")
            self.add_content("end")


    def process_reg(self, node: RegNode, fields: Sequence[FieldNode]) -> None:
        """
        Process a regular register
        """
        addr = self._get_address_str(node)
        conditional = self.get_addr_compare_conditional(addr)
        var = self.get_readback_data_var(addr)
        self.add_content(f"if({conditional}) begin")

        for field in fields:
            value = self.exp.dereferencer.get_value(field)
            if field.msb < field.lsb:
                # Field gets bitswapped since it is in [low:high] orientation
                value = do_bitswap(value)

            if field.width == 1:
                self.add_content(f"    {var}[{field.low}] = {value};")
            else:
                self.add_content(f"    {var}[{field.high}:{field.low}] = {value};")

        self.add_content("end")


    def process_buffered_reg(self, node: RegNode, regwidth: int, accesswidth: int) -> None:
        """
        Process a register which is fully buffered
        """
        rbuf = self.exp.read_buffering.get_rbuf_data(node)

        if accesswidth < regwidth:
            # Is wide reg
            n_subwords = regwidth // accesswidth
            subword_stride = accesswidth // 8
            for subword_idx in range(n_subwords):
                addr = self._get_address_str(node, subword_offset=subword_idx*subword_stride)
                conditional = self.get_addr_compare_conditional(addr)
                var = self.get_readback_data_var(addr)
                bslice = f"[{(subword_idx + 1) * accesswidth - 1}:{subword_idx*accesswidth}]"
                self.add_content(f"if({conditional}) begin")
                self.add_content(f"    {var} = {rbuf}{bslice};")
                self.add_content("end")
        else:
            # Is regular reg
            addr = self._get_address_str(node)
            conditional = self.get_addr_compare_conditional(addr)
            var = self.get_readback_data_var(addr)
            self.add_content(f"if({conditional}) begin")
            self.add_content(f"    {var}[{regwidth-1}:0] = {rbuf};")
            self.add_content("end")


    def process_wide_buffered_reg_with_bypass(self, node: RegNode, fields: Sequence[FieldNode], regwidth: int, accesswidth: int) -> None:
        """
        Special case for a wide buffered register where the register is its own
        trigger.

        First sub-word shall bypass the read buffer and assign directly.
        Subsequent subwords assign from the buffer.
        """

        # Generate assignments for first sub-word
        subword_assignments = self.get_wide_reg_subword_assignments(node, fields, regwidth, accesswidth)
        if subword_assignments[0]:
            addr = self._get_address_str(node, subword_offset=0)
            conditional = self.get_addr_compare_conditional(addr)
            self.add_content(f"if({conditional}) begin")
            for assignment in subword_assignments[0]:
                self.add_content("    " + assignment)
            self.add_content("end")

        # Assign remainder of subwords from read buffer
        n_subwords = regwidth // accesswidth
        subword_stride = accesswidth // 8
        rbuf = self.exp.read_buffering.get_rbuf_data(node)
        for subword_idx in range(1, n_subwords):
            addr = self._get_address_str(node, subword_offset=subword_idx*subword_stride)
            bslice = f"[{(subword_idx + 1) * accesswidth - 1}:{subword_idx*accesswidth}]"
            conditional = self.get_addr_compare_conditional(addr)
            var = self.get_readback_data_var(addr)
            self.add_content(f"if({conditional}) begin")
            self.add_content(f"    {var} = {rbuf}{bslice};")
            self.add_content("end")


    def get_wide_reg_subword_assignments(self, node: RegNode, fields: Sequence[FieldNode], regwidth: int, accesswidth: int) -> List[List[str]]:
        """
        Get a list of assignments for each subword

        Returns a 2d array where the first dimension indicates the subword index.
        The next dimension is the list of assignments
        """
        n_subwords = regwidth // accesswidth
        subword_stride = accesswidth // 8
        subword_assignments: List[List[str]] = [[] for _ in range(n_subwords)]

        # Fields are sorted by ascending low bit
        for field in fields:
            subword_idx = field.low // accesswidth

            if field.high < accesswidth * (subword_idx + 1):
                # entire field fits into this subword
                low = field.low - accesswidth * subword_idx
                high = field.high - accesswidth * subword_idx

                value = self.exp.dereferencer.get_value(field)
                if field.msb < field.lsb:
                    # Field gets bitswapped since it is in [low:high] orientation
                    value = do_bitswap(value)

                addr = self._get_address_str(node, subword_offset=subword_idx*subword_stride)
                var = self.get_readback_data_var(addr)
                subword_assignments[subword_idx].append(f"{var}[{high}:{low}] = {value};")

            else:
                # Field spans multiple sub-words
                # loop through subword indexes until the entire field has been assigned
                while field.high >= accesswidth * subword_idx:
                    # Allowable field window for this subword
                    subword_low = accesswidth * subword_idx
                    subword_high = subword_low + accesswidth - 1

                    # field slice (relative to reg)
                    f_low = max(subword_low, field.low)
                    f_high = min(subword_high, field.high)

                    # assignment slice
                    r_low = f_low - accesswidth * subword_idx
                    r_high = f_high - accesswidth * subword_idx

                    # Adjust to be relative to field
                    f_low -= field.low
                    f_high -= field.low

                    if field.msb < field.lsb:
                        # Field gets bitswapped since it is in [low:high] orientation
                        # Mirror the low/high indexes
                        f_low = field.width - 1 - f_low
                        f_high = field.width - 1 - f_high
                        f_low, f_high = f_high, f_low

                        value = do_bitswap(do_slice(self.exp.dereferencer.get_value(field), f_high, f_low))
                    else:
                        value = do_slice(self.exp.dereferencer.get_value(field), f_high, f_low)

                    addr = self._get_address_str(node, subword_offset=subword_idx*subword_stride)
                    var = self.get_readback_data_var(addr)
                    subword_assignments[subword_idx].append(f"{var}[{r_high}:{r_low}] = {value};")

                    # advance to the next subword
                    subword_idx += 1

        return subword_assignments


    def process_wide_reg(self, node: RegNode, fields: Sequence[FieldNode], regwidth: int, accesswidth: int) -> None:
        """
        Process a register whose accesswidth < regwidth
        """
        subword_assignments = self.get_wide_reg_subword_assignments(node, fields, regwidth, accesswidth)

        # Add generated content, wrapped in the address conditional
        subword_stride = accesswidth // 8
        for subword_idx, assignments in enumerate(subword_assignments):
            if not assignments:
                continue
            addr = self._get_address_str(node, subword_offset=subword_idx*subword_stride)
            conditional = self.get_addr_compare_conditional(addr)
            self.add_content(f"if({conditional}) begin")
            for assignment in assignments:
                self.add_content("    " + assignment)
            self.add_content("end")


    def exit_AddressableComponent(self, node: AddressableNode) -> None:
        super().exit_AddressableComponent(node)

        if not node.array_dimensions:
            return

        for _ in node.array_dimensions:
            self._array_stride_stack.pop()


class RetimedReadbackMuxGenerator(ReadbackMuxGenerator):
    """
    Alternate variant that is dedicated to building the 1st decode stage
    """

    def process_external_block(self, node: AddressableNode) -> None:
        # Do nothing. External blocks are handled in a completely separate readback mux
        pass

    def get_addr_compare_conditional(self, addr: str) -> str:
        # In the pipelined variant, compare the low-bits of both sides
        return f"ad_low(rd_mux_addr) == ad_low({addr})"

    def get_readback_data_var(self, addr: str) -> str:
        # In the pipelined variant, assign to the bin indexed by the high bits of addr
        return f"readback_data_var[ad_hi({addr})]"


class RetimedExtBlockReadbackMuxGenerator(ReadbackMuxGenerator):
    """
    When retiming is enabled, external blocks are implemented as a separate
    reaback mux that is not retimed using a partitioned address.

    This is because the address partitioning scheme used for individual register
    addresses does not work cleanly for address ranges. (not possible to cleanly
    map readback of a range to high-address data bins)

    Since the non-retimed mux generator already implements external ranges,
    re-use it and suppress generation of register logic.
    """

    def enter_Reg(self, node: RegNode) -> WalkerAction:
        return WalkerAction.SkipDescendants

    def process_external_block(self, node: AddressableNode) -> None:
        addr_lo = self._get_address_str(node)
        addr_hi = f"{addr_lo} + {SVInt(node.size - 1, self.exp.ds.addr_width)}"
        self.add_content(f"if((rd_mux_addr >= {addr_lo}) && (rd_mux_addr <= {addr_hi})) begin")
        data = self.exp.hwif.get_external_rd_data(node)
        self.add_content(f"    readback_data_var = {data};")
        self.add_content("    is_external_block_var = 1'b1;")
        self.add_content("end")
