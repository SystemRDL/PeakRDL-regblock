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
        return [
            "next_c = '0;",
            "load_next_c = '1;",
        ]
