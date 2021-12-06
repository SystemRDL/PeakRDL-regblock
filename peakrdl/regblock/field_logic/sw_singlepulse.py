from typing import TYPE_CHECKING, List

from .bases import NextStateConditional

if TYPE_CHECKING:
    from systemrdl.node import FieldNode

class Singlepulse(NextStateConditional):
    comment = "singlepulse clears back to 0"
    def is_match(self, field: 'FieldNode') -> bool:
        return field.get_property('singlepulse')

    def get_predicate(self, field: 'FieldNode') -> str:
        # TODO: make exporter promote this to an "else"?
        # Be mindful of sw/hw precedence. this would have to come last regardless
        return "1"

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)
        return [
            f"field_combo.{field_path}.next = '0;",
            f"field_combo.{field_path}.load_next = '1;",
        ]
