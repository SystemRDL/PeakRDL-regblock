from typing import TYPE_CHECKING, List

from systemrdl.node import Node, AddressableNode, RegNode, FieldNode

if TYPE_CHECKING:
    from ..exporter import RegblockExporter

class FieldLogic:
    def __init__(self, exporter:'RegblockExporter', top_node:Node):
        self.exporter = exporter
        self.top_node = top_node

        self._indent_level = 0

    def get_storage_struct(self) -> str:
        lines = []
        self._do_struct(lines, self.top_node, is_top=True)

        # Only declare the storage struct if it exists
        if lines:
            lines.append(f"{self._indent}field_storage_t field_storage;")
        return "\n".join(lines)

    def get_implementation(self) -> str:
        return "TODO:"

    #---------------------------------------------------------------------------
    # Field utility functions
    #---------------------------------------------------------------------------
    def get_storage_identifier(self, obj: FieldNode):
        assert obj.implements_storage

        return "TODO: implement get_storage_identifier()"


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

    def _do_struct(self, lines:List[str], node:AddressableNode, is_top:bool = False) -> bool:
        # Collect struct members first
        contents = []
        self._indent_level += 1
        for child in node.children():
            if isinstance(child, RegNode):
                self._do_reg_struct(contents, child)
            elif isinstance(child, AddressableNode):
                self._do_struct(contents, child)
        self._indent_level -= 1

        # If struct is not empty, emit a struct!
        if contents:
            if is_top:
                lines.append(f"{self._indent}typedef struct {{")
            else:
                lines.append(f"{self._indent}struct {{")

            lines.extend(contents)

            if is_top:
                lines.append(f"{self._indent}}} field_storage_t;")
            else:
                lines.append(f"{self._indent}}} {node.inst_name}{self._get_node_array_suffix(node)};")


    def _do_reg_struct(self, lines:List[str], node:RegNode) -> None:

        fields = []
        for field in node.fields():
            if field.implements_storage:
                fields.append(field)

        if not fields:
            return

        lines.append(f"{self._indent}struct {{")
        self._indent_level += 1
        for field in fields:
            if field.width == 1:
                lines.append(f"{self._indent}logic {field.inst_name};")
            else:
                lines.append(f"{self._indent}logic [{field.width-1}:0] {field.inst_name};")
        self._indent_level -= 1
        lines.append(f"{self._indent}}} {node.inst_name}{self._get_node_array_suffix(node)};")
