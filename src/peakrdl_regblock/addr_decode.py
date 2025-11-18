from typing import TYPE_CHECKING, Union, List, Optional

from systemrdl.node import FieldNode, RegNode, MemNode
from systemrdl.walker import WalkerAction

from .utils import (
    get_indexed_path,
    is_inside_external_block,
    has_sw_readable_descendants,
    has_sw_writable_descendants,
)
from .struct_generator import RDLStructGenerator
from .forloop_generator import RDLForLoopGenerator
from .identifier_filter import kw_filter as kwf
from .sv_int import SVInt

if TYPE_CHECKING:
    from .exporter import RegblockExporter
    from systemrdl.node import AddrmapNode, AddressableNode
    from systemrdl.node import RegfileNode

class AddressDecode:
    def __init__(self, exp:'RegblockExporter'):
        self.exp = exp

    @property
    def top_node(self) -> 'AddrmapNode':
        return self.exp.ds.top_node

    def get_strobe_struct(self) -> str:
        struct_gen = DecodeStructGenerator()
        s = struct_gen.get_struct(self.top_node, "decoded_reg_strb_t")
        assert s is not None # guaranteed to have at least one reg
        return s

    def get_implementation(self) -> str:
        gen = DecodeLogicGenerator(self)
        s = gen.get_content(self.top_node)
        assert s is not None
        return s

    def get_cpuif_index_logic(self) -> Optional[str]:
        """Generate cpuif_index calculation logic."""
        gen = CpuifIndexGenerator(self)
        return gen.get_content(self.top_node)

    def get_access_strobe(self, node: Union[RegNode, FieldNode], reduce_substrobes: bool=True) -> str:
        """
        Returns the Verilog string that represents the register/field's access strobe.
        """
        if isinstance(node, FieldNode):
            field = node
            path = get_indexed_path(self.top_node, node.parent)

            regwidth = node.parent.get_property('regwidth')
            accesswidth = node.parent.get_property('accesswidth')
            if regwidth > accesswidth:
                # Is wide register.
                # Determine the substrobe(s) relevant to this field
                sidx_hi = field.msb // accesswidth
                sidx_lo = field.lsb // accesswidth
                if sidx_hi == sidx_lo:
                    suffix = f"[{sidx_lo}]"
                else:
                    suffix = f"[{sidx_hi}:{sidx_lo}]"
                path += suffix

                if sidx_hi != sidx_lo and reduce_substrobes:
                    return "|decoded_reg_strb." + path

        else:
            path = get_indexed_path(self.top_node, node)

        return "decoded_reg_strb." + path

    def get_external_block_access_strobe(self, node: 'AddressableNode') -> str:
        assert node.external
        assert not isinstance(node, RegNode)
        path = get_indexed_path(self.top_node, node)
        return "decoded_reg_strb." + path


class DecodeStructGenerator(RDLStructGenerator):

    def _enter_external_block(self, node: 'AddressableNode') -> None:
        self.add_member(
            kwf(node.inst_name),
            array_dimensions=node.array_dimensions,
        )

    def enter_Addrmap(self, node: 'AddrmapNode') -> Optional[WalkerAction]:
        assert node.external
        self._enter_external_block(node)
        return WalkerAction.SkipDescendants

    def exit_Addrmap(self, node: 'AddrmapNode') -> None:
        assert node.external

    def enter_Regfile(self, node: 'RegfileNode') -> Optional[WalkerAction]:
        if node.external:
            self._enter_external_block(node)
            return WalkerAction.SkipDescendants
        super().enter_Regfile(node)
        return WalkerAction.Continue

    def exit_Regfile(self, node: 'RegfileNode') -> None:
        if node.external:
            return
        super().exit_Regfile(node)

    def enter_Mem(self, node: 'MemNode') -> Optional[WalkerAction]:
        assert node.external
        self._enter_external_block(node)
        return WalkerAction.SkipDescendants

    def exit_Mem(self, node: 'MemNode') -> None:
        assert node.external

    def enter_Reg(self, node: 'RegNode') -> None:
        # if register is "wide", expand the strobe to be able to access the sub-words
        n_subwords = node.get_property("regwidth") // node.get_property("accesswidth")

        self.add_member(
            kwf(node.inst_name),
            width=n_subwords,
            array_dimensions=node.array_dimensions,
        )

    # Stub out
    def exit_Reg(self, node: 'RegNode') -> None:
        pass
    def enter_Field(self, node: 'FieldNode') -> None:
        pass


class DecodeLogicGenerator(RDLForLoopGenerator):

    def __init__(self, addr_decode: AddressDecode) -> None:
        self.addr_decode = addr_decode
        super().__init__()

        # List of address strides for each dimension
        self._array_stride_stack = [] # type: List[int]

    def _add_addressablenode_decoding_flags(self, node: 'AddressableNode') -> None:
        addr_str = self._get_address_str(node)
        addr_decoding_str = f"cpuif_req_masked & (cpuif_addr >= {addr_str}) & (cpuif_addr <= {addr_str} + {SVInt(node.size - 1, self.addr_decode.exp.ds.addr_width)})"
        rhs = addr_decoding_str
        rhs_valid_addr = addr_decoding_str
        if isinstance(node, MemNode):
            readable = node.is_sw_readable
            writable = node.is_sw_writable
            if readable and writable:
                rhs_invalid_rw = "'0"
            elif readable and not writable:
                rhs = f"{addr_decoding_str} & !cpuif_req_is_wr"
                rhs_invalid_rw = f"{addr_decoding_str} & cpuif_req_is_wr"
            elif not readable and writable:
                rhs = f"{addr_decoding_str} & cpuif_req_is_wr"
                rhs_invalid_rw = f"{addr_decoding_str} & !cpuif_req_is_wr"
            else:
                raise RuntimeError
        # Add decoding flags
        self.add_content(f"{self.addr_decode.get_external_block_access_strobe(node)} = {rhs};")
        self.add_content(f"is_external |= {rhs};")
        if self.addr_decode.exp.ds.err_if_bad_addr:
            self.add_content(f"is_valid_addr |= {rhs_valid_addr};")
        if isinstance(node, MemNode):
            if self.addr_decode.exp.ds.err_if_bad_rw:
                self.add_content(f"is_invalid_rw |= {rhs_invalid_rw};")


    def enter_AddressableComponent(self, node: 'AddressableNode') -> Optional[WalkerAction]:
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
            self._add_addressablenode_decoding_flags(node)
            return WalkerAction.SkipDescendants

        return WalkerAction.Continue


    def _get_address_str(self, node: 'AddressableNode', subword_offset: int=0) -> str:
        expr_width = self.addr_decode.exp.ds.addr_width
        a = str(SVInt(
            node.raw_absolute_address - self.addr_decode.top_node.raw_absolute_address + subword_offset,
            expr_width
        ))
        for i, stride in enumerate(self._array_stride_stack):
            a += f" + ({expr_width})'(i{i}) * {SVInt(stride, expr_width)}"
        return a


    def _add_reg_decoding_flags(self,
        node: RegNode,
        subword_index: Union[int, None] = None,
        subword_stride: Union[int, None] = None) -> None:
        if subword_index is None or subword_stride is None:
            addr_decoding_str = f"cpuif_req_masked & (cpuif_addr == {self._get_address_str(node)})"
        else:
            addr_decoding_str = f"cpuif_req_masked & (cpuif_addr == {self._get_address_str(node, subword_offset=subword_index*subword_stride)})"
        rhs_valid_addr = addr_decoding_str
        readable = node.has_sw_readable
        writable = node.has_sw_writable
        if readable and writable:
            rhs = addr_decoding_str
            rhs_invalid_rw = "'0"
        elif readable and not writable:
            rhs = f"{addr_decoding_str} & !cpuif_req_is_wr"
            rhs_invalid_rw = f"{addr_decoding_str} & cpuif_req_is_wr"
        elif not readable and writable:
            rhs = f"{addr_decoding_str} & cpuif_req_is_wr"
            rhs_invalid_rw = f"{addr_decoding_str} & !cpuif_req_is_wr"
        else:
            raise RuntimeError
        # Add decoding flags
        if subword_index is None:
            self.add_content(f"{self.addr_decode.get_access_strobe(node)} = {rhs};")
        else:
            self.add_content(f"{self.addr_decode.get_access_strobe(node)}[{subword_index}] = {rhs};")
        if node.external:
            self.add_content(f"is_external |= {rhs};")
        if self.addr_decode.exp.ds.err_if_bad_addr:
            self.add_content(f"is_valid_addr |= {rhs_valid_addr};")
        if self.addr_decode.exp.ds.err_if_bad_rw:
            self.add_content(f"is_invalid_rw |= {rhs_invalid_rw};")

    def enter_Reg(self, node: RegNode) -> None:
        regwidth = node.get_property('regwidth')
        accesswidth = node.get_property('accesswidth')

        if regwidth == accesswidth:
            self._add_reg_decoding_flags(node)
        else:
            # Register is wide. Create a substrobe for each subword
            n_subwords = regwidth // accesswidth
            subword_stride = accesswidth // 8
            for i in range(n_subwords):
                self._add_reg_decoding_flags(node, i, subword_stride)

    def exit_AddressableComponent(self, node: 'AddressableNode') -> None:
        super().exit_AddressableComponent(node)

        if not node.array_dimensions:
            return

        for _ in node.array_dimensions:
            self._array_stride_stack.pop()


class CpuifIndexGenerator(RDLForLoopGenerator):
    """
    Generates cpuif_index calculation logic that maps each valid address
    to a sequential index (0, 1, 2, ...) regardless of address gaps.

    For arrays, generates: for(int i0=0; i0<dim; i0++) { if (addr == base + i0*stride) cpuif_index = base_idx + i0; }
    For single registers: if (addr == base) cpuif_index = idx;
    """

    def __init__(self, addr_decode: AddressDecode) -> None:
        self.addr_decode = addr_decode
        super().__init__()

        # Track sequential index for each valid address
        self.current_index = 0

        # List of address strides for each dimension (same as DecodeLogicGenerator)
        self._array_stride_stack: List[int] = []

        # Track base index when entering an array (for calculating offset)
        self._base_index_stack: List[int] = []
        # Track index stride for each array dimension (number of indices per instance)
        # This is calculated in pop_loop(), similar to readback generator
        self._index_stride_stack: List[tuple] = []
        # Track start index for each loop level (similar to readback generator's start_offset_stack)
        self._start_index_stack: List[int] = []
        # Track dimensions for each loop level
        self._dim_stack: List[int] = []

    def _get_address_str(self, node: "AddressableNode", subword_offset: int = 0) -> str:
        """Generate address string, handling array dimensions."""
        expr_width = self.addr_decode.exp.ds.addr_width
        base_addr = (
            node.raw_absolute_address
            - self.addr_decode.top_node.raw_absolute_address
            + subword_offset
        )

        if len(self._array_stride_stack):
            # For arrays, generate: base + i0*stride0 + i1*stride1 + ...
            a = str(SVInt(base_addr, expr_width))
            for i, stride in enumerate(self._array_stride_stack):
                a += f" + ({expr_width})'(i{i}) * {SVInt(stride, expr_width)}"
        else:
            # Single element
            a = str(SVInt(base_addr, expr_width))
        return a

    def push_loop(self, dim: int) -> None:
        """Override to track start index for stride calculation."""
        super().push_loop(dim)
        self._start_index_stack.append(self.current_index)
        self._dim_stack.append(dim)

    def pop_loop(self) -> None:
        """Override to calculate stride when exiting loop."""
        start_index = self._start_index_stack.pop()
        dim = self._dim_stack.pop()

        # Number of indices used by registers enclosed in this loop
        # This is calculated BEFORE advancing current_index
        n_indices = self.current_index - start_index

        # Store stride for this loop level (for replacing placeholder tokens)
        # loop_idx is the index of the loop variable (0 for i0, 1 for i1, etc.)
        # _loop_level is the nesting level (1 when inside first loop, 2 when inside second, etc.)
        # So loop_idx = _loop_level - 1
        # Calculate loop_idx BEFORE calling super().pop_loop() which decrements _loop_level
        loop_idx = self._loop_level - 1

        # Replace placeholder in loop body's children now (before it's popped)
        loop_body = self.current_loop
        placeholder = f"$i{loop_idx}sz"
        self._index_stride_stack.append((placeholder, n_indices))

        # Replace placeholder in loop body's children before popping
        for i, child in enumerate(loop_body.children):
            if isinstance(child, str):
                loop_body.children[i] = child.replace(f"$i{loop_idx}sz", str(n_indices))

        super().pop_loop()

        # Advance current_index to account for loop's contents (all instances)
        self.current_index = start_index + n_indices * dim

    def enter_AddressableComponent(
        self, node: "AddressableNode"
    ) -> Optional[WalkerAction]:
        super().enter_AddressableComponent(node)

        if node.array_dimensions:
            # Collect strides for each array dimension
            assert node.array_stride is not None
            current_stride = node.array_stride
            strides = []
            for dim in reversed(node.array_dimensions):
                strides.append(current_stride)
                current_stride *= dim
            strides.reverse()
            self._array_stride_stack.extend([s for s in strides if s is not None])
            # Store base index when entering array (for reference, but stride is calculated in pop_loop)
            self._base_index_stack.append(self.current_index)

        return WalkerAction.Continue

    def exit_AddressableComponent(self, node: "AddressableNode") -> None:
        super().exit_AddressableComponent(node)

        if not node.array_dimensions:
            return

        for _ in node.array_dimensions:
            self._array_stride_stack.pop()
            if self._base_index_stack:
                # Just pop - stride was already calculated in pop_loop()
                self._base_index_stack.pop()

    def start(self) -> None:
        """Initialize the generator with cpuif_index declaration."""
        super().start()
        # Add cpuif_index declaration at the beginning
        self.add_content("integer cpuif_index;")
        self.add_content("")
        self.add_content("always @(*) begin")
        self.add_content("    cpuif_index = 0;")

    def finish(self) -> Optional[str]:
        """Close the always block and replace placeholder tokens."""
        self.add_content("end")
        result = super().finish()
        if result is None:
            return None
        # Replace placeholder tokens like $i0sz with actual stride values
        # Process in reverse order to handle nested loops correctly
        for placeholder, stride in reversed(self._index_stride_stack):
            result = result.replace(placeholder, str(stride))
        return result

    def _process_external_block(self, node: "AddressableNode") -> None:
        """
        Generate cpuif_index assignment for external blocks (regfile, addrmap, mem).
        All addresses within the block map to the same index since external blocks
        use a single shared rd_data signal.
        """
        addr_str = self._get_address_str(node)
        addr_width = self.addr_decode.exp.ds.addr_width
        block_size = node.size
        base_index = self.current_index

        # Generate address range check: all addresses in block map to same index
        addr_low = addr_str
        addr_high = f"{addr_str} + {SVInt(block_size - 1, addr_width)}"
        self.add_content(
            f"    if ((cpuif_addr >= {addr_low}) && (cpuif_addr <= {addr_high})) begin"
        )
        self.add_content(f"        cpuif_index = {base_index};")
        self.add_content("    end")
        # Increment index once for the single shared readback slot
        self.current_index += 1

    def enter_Regfile(self, node: "RegfileNode") -> Optional[WalkerAction]:
        # For regblock, just check node.external directly (no flattening logic)
        if not node.external:
            return WalkerAction.Continue

        self._process_external_block(node)
        return WalkerAction.SkipDescendants

    def enter_Addrmap(self, node: "AddrmapNode") -> Optional[WalkerAction]:
        if node == self.addr_decode.top_node:
            return WalkerAction.Continue

        # For regblock, just check node.external directly (no flattening logic)
        if not node.external:
            return WalkerAction.Continue

        self._process_external_block(node)
        return WalkerAction.SkipDescendants

    def enter_Mem(self, node: "MemNode") -> None:
        if not node.external:
            return

        # External memory: all entries map to the same index
        # External memory uses a single rd_data signal, so all entries
        # share the same readback array slot
        addr_str = self._get_address_str(node)
        addr_width = self.addr_decode.exp.ds.addr_width
        memwidth = node.get_property("memwidth")
        mementries = node.get_property("mementries")

        # Calculate address stride (bytes per entry)
        entry_stride = memwidth // 8

        base_index = self.current_index

        if len(self._array_stride_stack):
            # Arrayed memory - handled by loop structure
            # The loop will be generated by the parent, we just need to generate
            # the inner loop for memory entries
            pass
        else:
            # Single memory - generate for loop for each entry
            # All entries map to the same base_index (not base_index + loop_var)
            # because external memory uses a single rd_data signal
            # Use loop variable based on current nesting level to avoid shadowing
            loop_var = f"i{self._loop_level}"
            self.add_content(
                f"    for(int {loop_var}=0; {loop_var}<{mementries}; {loop_var}++) begin"
            )
            entry_addr = f"{addr_str} + {loop_var}*{SVInt(entry_stride, addr_width)}"
            self.add_content(f"        if (cpuif_addr == {entry_addr}) begin")
            self.add_content(f"            cpuif_index = {base_index};")
            self.add_content("        end")
            self.add_content("    end")
            # Only increment once for the single shared readback slot
            self.current_index += 1

    def enter_Reg(self, node: RegNode) -> Optional[WalkerAction]:
        # Skip registers inside external blocks (handled by parent)
        # But process standalone external registers (they still need indices)
        if is_inside_external_block(node, self.addr_decode.top_node):
            return WalkerAction.SkipDescendants

        regwidth = node.get_property("regwidth")
        accesswidth = node.get_property("accesswidth")

        # Only generate index for readable or writable registers
        if not (node.has_sw_readable or node.has_sw_writable):
            return WalkerAction.SkipDescendants

        # External registers are handled the same way as normal registers for index calculation

        base_index = self.current_index

        # Use register's own array_dimensions, not parent array dimensions
        array_dims = node.array_dimensions if node.array_dimensions else []

        # Check if we're already inside a loop created by enter_AddressableComponent for this register
        already_in_register_loop = (
            array_dims and self._loop_level > 0 and self._loop_level <= len(array_dims)
        )

        # If we're inside an arrayed component (parent arrayed component, not this register's own loop),
        # we need to account for the outer loop variable
        index_offset_str = ""
        if self._base_index_stack and not already_in_register_loop:
            loop_idx = self._loop_level - 1 if self._loop_level > 0 else 0
            if already_in_register_loop:
                loop_idx = self._loop_level - 2 if self._loop_level > 1 else 0
            index_offset_str = f" + i{loop_idx}*$i{loop_idx}sz"

        # Get base address (relative to top)
        base_addr = (
            node.raw_absolute_address - self.addr_decode.top_node.raw_absolute_address
        )
        addr_width = self.addr_decode.exp.ds.addr_width

        # Calculate address stride (bytes per register)
        # For register arrays, stride depends on whether the register is wide:
        # - Normal register: stride = accesswidth/8 (typically 4 bytes for 32-bit)
        # - Wide register: stride = regwidth/8 (typically 8 bytes for 64-bit accessed as 32-bit)
        # The array_stride_stack is for nested array dimensions, not register stride
        # For arrayed registers, we need the stride between array elements, which is the register width
        addr_stride = regwidth // 8  # Use regwidth for array stride, not accesswidth

        if regwidth == accesswidth:
            # Normal register (not wide)
            if array_dims and not already_in_register_loop:
                # Arrayed register - generate for loop for first dimension
                dim = array_dims[0] if len(array_dims) > 0 else 1
                loop_var = f"i{self._loop_level}"
                reg_base_addr = (
                    node.raw_absolute_address
                    - self.addr_decode.top_node.raw_absolute_address
                )
                if self._base_index_stack:
                    first_reg_base_str = str(SVInt(reg_base_addr, addr_width))
                    for i, stride in enumerate(self._array_stride_stack):
                        first_reg_base_str += f" + ({addr_width})'(i{i}) * {SVInt(stride, addr_width)}"
                else:
                    first_reg_base_str = str(SVInt(reg_base_addr, addr_width))
                self.add_content(
                    f"    for(int {loop_var}=0; {loop_var}<{dim}; {loop_var}++) begin"
                )
                addr_expr = f"{first_reg_base_str} + {loop_var}*{SVInt(addr_stride, addr_width)}"
                self.add_content(f"        if (cpuif_addr == {addr_expr}) begin")
                self.add_content(
                    f"            cpuif_index = {base_index} + {loop_var}{index_offset_str};"
                )
                self.add_content("        end")
                self.add_content("    end")
                # Advance index by array size
                total_size = 1
                for d in array_dims:
                    total_size *= d
                self.current_index += total_size
            elif array_dims and already_in_register_loop:
                # Arrayed register, but we're already inside a loop created by enter_AddressableComponent
                dim = array_dims[0] if len(array_dims) > 0 else 1
                loop_var = f"i{self._loop_level - 1}"
                reg_base_addr = (
                    node.raw_absolute_address
                    - self.addr_decode.top_node.raw_absolute_address
                )
                addr_expr = f"{SVInt(reg_base_addr, addr_width)} + {loop_var}*{SVInt(addr_stride, addr_width)}"
                self.add_content(f"    if (cpuif_addr == {addr_expr}) begin")
                self.add_content(f"        cpuif_index = {base_index} + {loop_var};")
                self.add_content("    end")
                self.current_index += 1
            else:
                # Single register - use _get_address_str to include outer loop variables
                addr_expr = self._get_address_str(node, 0)
                self.add_content(f"    if (cpuif_addr == {addr_expr}) begin")
                self.add_content(
                    f"        cpuif_index = {base_index}{index_offset_str};"
                )
                self.add_content("    end")
                self.current_index += 1
        else:
            # Wide register - generate index for each subword
            n_subwords = regwidth // accesswidth
            subword_stride = accesswidth // 8

            if array_dims and not already_in_register_loop:
                # Arrayed wide register - generate nested loops
                dim = array_dims[0] if len(array_dims) > 0 else 1
                loop_var = f"i{self._loop_level}"
                for subword_idx in range(n_subwords):
                    if self._base_index_stack:
                        reg_base_addr = (
                            node.raw_absolute_address
                            - self.addr_decode.top_node.raw_absolute_address
                            + subword_idx * subword_stride
                        )
                        base_addr_str = str(SVInt(reg_base_addr, addr_width))
                        for i, stride in enumerate(self._array_stride_stack):
                            base_addr_str += f" + ({addr_width})'(i{i}) * {SVInt(stride, addr_width)}"
                    else:
                        base_addr_str = self._get_address_str(
                            node, subword_idx * subword_stride
                        )
                    self.add_content(
                        f"    for(int {loop_var}=0; {loop_var}<{dim}; {loop_var}++) begin"
                    )
                    addr_expr = (
                        f"{base_addr_str} + {loop_var}*{SVInt(addr_stride, addr_width)}"
                    )
                    self.add_content(f"        if (cpuif_addr == {addr_expr}) begin")
                    self.add_content(
                        f"            cpuif_index = {base_index} + {loop_var}*{n_subwords} + {subword_idx}{index_offset_str};"
                    )
                    self.add_content("        end")
                    self.add_content("    end")
                # Advance index by array_size * n_subwords
                total_size = 1
                for d in array_dims:
                    total_size *= d
                self.current_index += total_size * n_subwords
            elif array_dims and already_in_register_loop:
                # Arrayed wide register, but we're already inside a loop created by enter_AddressableComponent
                dim = array_dims[0] if len(array_dims) > 0 else 1
                loop_var = f"i{self._loop_level - 1}"
                for subword_idx in range(n_subwords):
                    reg_base_addr = (
                        node.raw_absolute_address
                        - self.addr_decode.top_node.raw_absolute_address
                        + subword_idx * subword_stride
                    )
                    addr_expr = f"{SVInt(reg_base_addr, addr_width)} + {loop_var}*{SVInt(addr_stride, addr_width)}"
                    self.add_content(f"    if (cpuif_addr == {addr_expr}) begin")
                    self.add_content(
                        f"        cpuif_index = {base_index} + {loop_var}*{n_subwords} + {subword_idx};"
                    )
                    self.add_content("    end")
                self.current_index += n_subwords
            else:
                # Single wide register - generate for each subword
                for subword_idx in range(n_subwords):
                    addr_expr = self._get_address_str(
                        node, subword_idx * subword_stride
                    )
                    self.add_content(f"    if (cpuif_addr == {addr_expr}) begin")
                    self.add_content(
                        f"        cpuif_index = {base_index + subword_idx}{index_offset_str};"
                    )
                    self.add_content("    end")
                self.current_index += n_subwords

        return WalkerAction.SkipDescendants
