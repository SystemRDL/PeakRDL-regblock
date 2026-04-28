from typing import TYPE_CHECKING, Optional

from systemrdl.walker import WalkerAction


from .forloop_generator import RDLForLoopGenerator

if TYPE_CHECKING:
    from .exporter import RegblockExporter
    from systemrdl.node import FieldNode, AddressableNode, AddrmapNode


class ParityErrorReduceGenerator(RDLForLoopGenerator):
    def __init__(self, exp: 'RegblockExporter') -> None:
        super().__init__()
        self.exp = exp

    def get_implementation(self) -> str:
        content = self.get_content(self.exp.ds.top_node)
        if content is None:
            return ""
        return content

    def enter_AddressableComponent(self, node: 'AddressableNode') -> WalkerAction:
        super().enter_AddressableComponent(node)
        if node.external:
            return WalkerAction.SkipDescendants
        return WalkerAction.Continue

    def enter_Field(self, node: 'FieldNode') -> None:
        if node.get_property('paritycheck') and node.implements_storage:
            self.add_content(
                f"err |= {self.exp.field_logic.get_parity_error_identifier(node)};"
            )


def parity_path_id(top_node: 'AddrmapNode', field: 'FieldNode', byte: Optional[int] = None) -> str:
    """Build an SV-legal identifier suffix from a field path, e.g.:

        r1.f1            -> 'R1_F1'
        r2[3].f1         -> 'R2_3_F1'
        r2[i0].f1, byte=2 -> 'R2_I0_F1_BYTE2'

    Used to construct FERR_IDX_<id> and PINJ_IDX_<id>_BYTE<i> localparam names.
    """
    from .utils import get_indexed_path
    path = get_indexed_path(top_node, field)
    # Replace `.`, `[`, `]` with `_`. Strip trailing `_`.
    sv_id = path.replace('.', '_').replace('[', '_').replace(']', '').upper()
    sv_id = sv_id.rstrip('_')
    if byte is not None:
        sv_id = f"{sv_id}_BYTE{byte}"
    return sv_id
