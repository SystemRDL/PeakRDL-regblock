from typing import TYPE_CHECKING, Optional

from systemrdl.walker import WalkerAction


from .forloop_generator import RDLForLoopGenerator

if TYPE_CHECKING:
    from .exporter import RegblockExporter, DesignState
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


class BytewiseParityModuleGenerator:
    """
    Emits the SV that lives in module_tmpl.sv when --parity-byte is on:
      - per-field error reducer (OR of mismatch bytes)
      - per-parity-bit one-hot inject decoder
      - sticky field_parity_error always_ff
    """

    def __init__(self, exp: 'RegblockExporter') -> None:
        self.exp = exp

    @property
    def ds(self) -> 'DesignState':
        return self.exp.ds

    def get_inject_decode(self) -> str:
        """Combinational decoder: drives field_combo.<path>.inject_hit[i] for each parity bit."""
        if not self.ds.has_bytewise_parity:
            return ""
        fl = self.exp.field_logic
        lines = []
        for (node, byte, _lo, _hi, pinj_idx, _ferr_idx) in self.ds.parity_bits:
            ident = fl.get_parity_byte_inject_hit_identifier(node, byte)
            lines.append(
                f"assign {ident} = parity_inject_strobe & "
                f"(parity_inject_sel == {pinj_idx});"
            )
        return "\n".join(lines)

    def get_field_error_reducers(self) -> str:
        """For each parity field, OR all its mismatch bytes into a single combinational signal."""
        if not self.ds.has_bytewise_parity:
            return ""
        fl = self.exp.field_logic
        lines = []
        for (node, byte_count, ferr_idx, _first_pinj) in self.ds.parity_fields:
            ident = parity_path_id(self.ds.top_node, node)
            mismatch_terms = " | ".join(
                fl.get_parity_byte_mismatch_identifier(node, b)
                for b in range(byte_count)
            )
            lines.append(f"logic field_parity_mismatch_{ident};")
            lines.append(f"assign field_parity_mismatch_{ident} = {mismatch_terms};")
        return "\n".join(lines)

    def get_sticky_latch_block(self) -> str:
        """Always_ff that latches each per-field mismatch into the sticky field_parity_error vector."""
        if not self.ds.has_bytewise_parity:
            return ""
        lines = []
        for (node, _bc, ferr_idx, _fp) in self.ds.parity_fields:
            ident = parity_path_id(self.ds.top_node, node)
            lines.append(
                f"if (error_clear_i) field_parity_error[{ferr_idx}] <= 1'b0;"
            )
            lines.append(
                f"else if (field_parity_mismatch_{ident}) "
                f"field_parity_error[{ferr_idx}] <= 1'b1;"
            )
        return "\n".join(lines)


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
