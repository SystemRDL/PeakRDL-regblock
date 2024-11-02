from typing import TYPE_CHECKING, List

from systemrdl.rdltypes import InterruptType

from .bases import NextStateConditional
from ..vhdl_int import VhdlInt

if TYPE_CHECKING:
    from systemrdl.node import FieldNode


class Sticky(NextStateConditional):
    """
    Normal multi-bit sticky
    """
    comment = "multi-bit sticky"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and field.get_property('sticky')
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        I = self.exp.hwif.get_input_identifier(field)
        R = self.exp.field_logic.get_storage_identifier(field)
        zero = VhdlInt.zeros(field.width)
        return f"({R} = {zero}) and ({I} /= {zero})"

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        I = self.exp.hwif.get_input_identifier(field)
        return [
            f"next_c := {I};",
            "load_next_c := '1';",
        ]


class Stickybit(NextStateConditional):
    """
    Normal stickybit
    """
    comment = "stickybit"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and field.get_property('stickybit')
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        F = self.exp.hwif.get_input_identifier(field)
        zero = VhdlInt.zeros(field.width)
        return f"{F} /= {zero}"

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        I = self.exp.hwif.get_input_identifier(field)
        R = self.exp.field_logic.get_storage_identifier(field)
        return [
            f"next_c := {R} or {I};",
            "load_next_c := '1';",
        ]

class PosedgeStickybit(NextStateConditional):
    """
    Positive edge stickybit
    """
    comment = "posedge stickybit"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and field.get_property('stickybit')
            and field.get_property('intr type') == InterruptType.posedge
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        I = self.exp.hwif.get_input_identifier(field)
        Iq = self.exp.field_logic.get_next_q_identifier(field)
        zero = VhdlInt.zeros(field.width)
        return f"(not {Iq} and {I}) /= {zero}"

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        I = self.exp.hwif.get_input_identifier(field)
        Iq = self.exp.field_logic.get_next_q_identifier(field)
        R = self.exp.field_logic.get_storage_identifier(field)
        return [
            f"next_c := {R} or (not {Iq} and {I});",
            "load_next_c := '1';",
        ]

class NegedgeStickybit(NextStateConditional):
    """
    Negative edge stickybit
    """
    comment = "negedge stickybit"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and field.get_property('stickybit')
            and field.get_property('intr type') == InterruptType.negedge
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        I = self.exp.hwif.get_input_identifier(field)
        Iq = self.exp.field_logic.get_next_q_identifier(field)
        zero = VhdlInt.zeros(field.width)
        return f"({Iq} and not {I}) /= {zero}"

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        I = self.exp.hwif.get_input_identifier(field)
        Iq = self.exp.field_logic.get_next_q_identifier(field)
        R = self.exp.field_logic.get_storage_identifier(field)
        return [
            f"next_c := {R} or ({Iq} and not {I});",
            "load_next_c := '1';",
        ]

class BothedgeStickybit(NextStateConditional):
    """
    edge-sensitive stickybit
    """
    comment = "bothedge stickybit"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and field.get_property('stickybit')
            and field.get_property('intr type') == InterruptType.bothedge
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        I = self.exp.hwif.get_input_identifier(field)
        Iq = self.exp.field_logic.get_next_q_identifier(field)
        return f"{Iq} /= {I}"

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        I = self.exp.hwif.get_input_identifier(field)
        Iq = self.exp.field_logic.get_next_q_identifier(field)
        R = self.exp.field_logic.get_storage_identifier(field)
        return [
            f"next_c := {R} or ({Iq} xor {I});",
            "load_next_c := '1';",
        ]

class PosedgeNonsticky(NextStateConditional):
    """
    Positive edge non-stickybit
    """
    is_unconditional = True
    comment = "posedge nonsticky"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and not field.get_property('stickybit')
            and field.get_property('intr type') == InterruptType.posedge
        )

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        I = self.exp.hwif.get_input_identifier(field)
        Iq = self.exp.field_logic.get_next_q_identifier(field)
        return [
            f"next_c := not {Iq} and {I};",
            "load_next_c := '1';",
        ]

class NegedgeNonsticky(NextStateConditional):
    """
    Negative edge non-stickybit
    """
    is_unconditional = True
    comment = "negedge nonsticky"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and not field.get_property('stickybit')
            and field.get_property('intr type') == InterruptType.negedge
        )

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        I = self.exp.hwif.get_input_identifier(field)
        Iq = self.exp.field_logic.get_next_q_identifier(field)
        return [
            f"next_c := {Iq} and not {I};",
            "load_next_c := '1';",
        ]

class BothedgeNonsticky(NextStateConditional):
    """
    edge-sensitive non-stickybit
    """
    is_unconditional = True
    comment = "bothedge nonsticky"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and not field.get_property('stickybit')
            and field.get_property('intr type') == InterruptType.bothedge
        )

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        I = self.exp.hwif.get_input_identifier(field)
        Iq = self.exp.field_logic.get_next_q_identifier(field)
        return [
            f"next_c := {Iq} xor {I};",
            "load_next_c := '1';",
        ]
