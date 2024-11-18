from typing import TYPE_CHECKING, Union, List, Optional

from systemrdl.node import FieldNode, RegNode
from systemrdl.walker import WalkerAction

from .utils import get_indexed_path
from .struct_generator import RDLFlatStructGenerator
from .forloop_generator import RDLForLoopGenerator
from .identifier_filter import kw_filter as kwf
from .vhdl_int import VhdlInt

if TYPE_CHECKING:
    from .exporter import RegblockExporter
    from systemrdl.node import Node, AddrmapNode, AddressableNode
    from systemrdl.node import RegfileNode, MemNode

class AddressDecode:
    def __init__(self, exp:'RegblockExporter'):
        self.exp = exp

    @property
    def top_node(self) -> 'AddrmapNode':
        return self.exp.ds.top_node

    def get_strobe_struct(self) -> str:
        struct_gen = DecodeStructGenerator(self)
        s = struct_gen.get_struct(self.top_node, "decoded_reg_strb_t")
        assert s is not None # guaranteed to have at least one reg
        return s

    def get_implementation(self) -> str:
        gen = DecodeLogicGenerator(self)
        s = gen.get_content(self.top_node)
        assert s is not None
        return s

    def get_access_strobe(self, node: Union[RegNode, FieldNode], reduce_substrobes: bool=True) -> str:
        """
        Returns the VHDL string that represents the register/field's access strobe.
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
                    suffix = f"({sidx_lo})"
                else:
                    suffix = f"({sidx_hi} downto {sidx_lo})"
                path += suffix

                if sidx_hi != sidx_lo and reduce_substrobes:
                    return "or decoded_reg_strb." + path

        else:
            path = get_indexed_path(self.top_node, node)

        return "decoded_reg_strb." + path

    def get_external_block_access_strobe(self, node: 'AddressableNode') -> str:
        assert node.external
        assert not isinstance(node, RegNode)
        path = get_indexed_path(self.top_node, node)
        return "decoded_reg_strb." + path


class DecodeStructGenerator(RDLFlatStructGenerator):

    def __init__(self, address_decode: 'AddressDecode') -> None:
        super().__init__()
        self.top_node = address_decode.top_node

    def get_typdef_name(self, node:'Node', suffix: str = "") -> str:
        base = node.get_rel_path(
            self.top_node.parent,
            hier_separator=".",
            array_suffix="",
            empty_array_suffix=""
        )
        return kwf(f'{base}{suffix}_strb_t')

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


    def enter_AddressableComponent(self, node: 'AddressableNode') -> Optional[WalkerAction]:
        super().enter_AddressableComponent(node)

        if node.is_array:
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
            addr_str = self._get_address_str(node)
            strb = self.addr_decode.get_external_block_access_strobe(node)
            rhs = f"cpuif_req_masked and to_std_logic(to_unsigned(cpuif_addr) >= {addr_str} and to_unsigned(cpuif_addr) <= {addr_str} + {VhdlInt.integer_hex(node.size - 1)})"
            self.add_content(f"{strb} <= {rhs};")
            self.add_content(f"is_external := is_external or ({rhs});")
            return WalkerAction.SkipDescendants

        return WalkerAction.Continue


    def _get_address_str(self, node: 'AddressableNode', subword_offset: int=0) -> str:
        a = str(VhdlInt.integer_hex(
            node.raw_absolute_address - self.addr_decode.top_node.raw_absolute_address + subword_offset,
        ))
        for i, stride in enumerate(self._array_stride_stack):
            a += f" + i{i}*{VhdlInt.integer_hex(stride)}"
        return a


    def enter_Reg(self, node: RegNode) -> None:
        regwidth = node.get_property('regwidth')
        accesswidth = node.get_property('accesswidth')

        if regwidth == accesswidth:
            rhs = f"cpuif_req_masked and (cpuif_addr = {self._get_address_str(node)})"
            s = f"{self.addr_decode.get_access_strobe(node)} <= {rhs};"
            self.add_content(s)
            if node.external:
                readable = node.has_sw_readable
                writable = node.has_sw_writable
                if readable and writable:
                    self.add_content(f"is_external := is_external or ({rhs});")
                elif readable and not writable:
                    self.add_content(f"is_external := is_external or ({rhs}) and not cpuif_req_is_wr;")
                elif not readable and writable:
                    self.add_content(f"is_external := is_external or ({rhs}) and cpuif_req_is_wr;")
                else:
                    raise RuntimeError
        else:
            # Register is wide. Create a substrobe for each subword
            n_subwords = regwidth // accesswidth
            subword_stride = accesswidth // 8
            for i in range(n_subwords):
                rhs = f"cpuif_req_masked and (cpuif_addr = {self._get_address_str(node, subword_offset=(i*subword_stride))})"
                s = f"{self.addr_decode.get_access_strobe(node)}({i}) <= {rhs};"
                self.add_content(s)
                if node.external:
                    readable = node.has_sw_readable
                    writable = node.has_sw_writable
                    if readable and writable:
                        self.add_content(f"is_external := is_external or ({rhs});")
                    elif readable and not writable:
                        self.add_content(f"is_external := is_external or ({rhs}) and not cpuif_req_is_wr;")
                    elif not readable and writable:
                        self.add_content(f"is_external := is_external or ({rhs}) and cpuif_req_is_wr;")
                    else:
                        raise RuntimeError

    def exit_AddressableComponent(self, node: 'AddressableNode') -> None:
        super().exit_AddressableComponent(node)

        if not node.is_array:
            return

        for _ in node.array_dimensions:
            self._array_stride_stack.pop()
