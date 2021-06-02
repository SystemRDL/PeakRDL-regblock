import re
from typing import TYPE_CHECKING, List

from systemrdl.node import Node, AddressableNode, RegNode


if TYPE_CHECKING:
    from .exporter import RegblockExporter

class AddressDecode:
    def __init__(self, exporter:'RegblockExporter', top_node:AddressableNode):
        self.exporter = exporter
        self.top_node = top_node

        self._indent_level = 0

        # List of address strides for each dimension
        self._array_stride_stack = []

    def get_strobe_struct(self) -> str:
        lines = []
        self._do_struct(lines, self.top_node, is_top=True)
        return "\n".join(lines)

    def get_implementation(self) -> str:
        lines = []
        self._do_address_decode_node(lines, self.top_node)
        return "\n".join(lines)


    #---------------------------------------------------------------------------
    # Struct generation functions
    #---------------------------------------------------------------------------
    @property
    def _indent(self) -> str:
        return "    " * self._indent_level

    def _get_node_array_suffix(self, node:AddressableNode) -> str:
        if node.is_array:
            return "".join([f'[{dim}]' for dim in node.array_dimensions])
        return ""

    def _do_struct(self, lines:List[str], node:AddressableNode, is_top:bool = False) -> None:
        if is_top:
            lines.append(f"{self._indent}typedef struct {{")
        else:
            lines.append(f"{self._indent}struct {{")

        self._indent_level += 1
        for child in node.children():
            if isinstance(child, RegNode):
                lines.append(f"{self._indent}logic {child.inst_name}{self._get_node_array_suffix(child)};")
            elif isinstance(child, AddressableNode):
                self._do_struct(lines, child)
        self._indent_level -= 1

        if is_top:
            lines.append(f"{self._indent}}} access_strb_t;")
        else:
            lines.append(f"{self._indent}}} {node.inst_name}{self._get_node_array_suffix(node)};")

    #---------------------------------------------------------------------------
    # Access strobe generation functions
    #---------------------------------------------------------------------------

    def _push_array_dims(self, lines:List[str], node:AddressableNode):
        if not node.is_array:
            return

        # Collect strides for each array dimension
        current_stride = node.array_stride
        strides = []
        for dim in reversed(node.array_dimensions):
            strides.append(current_stride)
            current_stride *= dim
        strides.reverse()

        for dim, stride in zip(node.array_dimensions, strides):
            iterator = "i%d" % len(self._array_stride_stack)
            self._array_stride_stack.append(stride)
            lines.append(f"{self._indent}for(int {iterator}=0; {iterator}<{dim}; {iterator}++) begin")
            self._indent_level += 1

    def _pop_array_dims(self, lines:List[str], node:AddressableNode):
        if not node.is_array:
            return

        for _ in node.array_dimensions:
            self._array_stride_stack.pop()
            self._indent_level -= 1
            lines.append(f"{self._indent}end")

    def _get_address_str(self, node:AddressableNode) -> str:
        a = "'h%x" % (node.raw_absolute_address - self.top_node.raw_absolute_address)
        for i, stride in enumerate(self._array_stride_stack):
            a += f" + i{i}*'h{stride:x}"
        return a

    def _get_strobe_str(self, node:AddressableNode) -> str:
        path = node.get_rel_path(self.top_node, array_suffix="[!]", empty_array_suffix="[!]")

        class repl:
            def __init__(self):
                self.i = 0
            def __call__(self, match):
                s = f'i{self.i}'
                self.i += 1
                return s

        path = re.sub(r'!', repl(), path)
        strb = "access_strb." + path
        return strb

    def _do_address_decode_node(self, lines:List[str], node:AddressableNode) -> None:
        for child in node.children():
            if isinstance(child, RegNode):
                self._push_array_dims(lines, child)
                lines.append(f"{self._indent}{self._get_strobe_str(child)} = cpuif_req & (cpuif_addr == {self._get_address_str(child)});")
                self._pop_array_dims(lines, child)
            elif isinstance(child, AddressableNode):
                self._push_array_dims(lines, child)
                self._do_address_decode_node(lines, child)
                self._pop_array_dims(lines, child)
