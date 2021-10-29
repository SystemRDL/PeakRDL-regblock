from typing import TYPE_CHECKING, List

from .bases import NextStateConditional

if TYPE_CHECKING:
    from systemrdl.node import FieldNode


class HWSet(NextStateConditional):
    comment = "HW Set"
    def is_match(self, field: 'FieldNode') -> bool:
        return bool(field.get_property('hwset'))

    def get_predicate(self, field: 'FieldNode') -> str:
        prop = field.get_property('hwset')
        if isinstance(prop, bool):
            identifier = self.exp.hwif.get_implied_prop_input_identifier(field, "hwset")
        else:
            # signal or field
            identifier = self.exp.dereferencer.get_value(prop)
        return identifier

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)

        hwmask = field.get_property('hwmask')
        hwenable = field.get_property('hwenable')
        R = f"field_storage.{field_path}"
        if hwmask is not None:
            M = self.exp.dereferencer.get_value(hwmask)
            next_val = f"{R} | ~{M}"
        elif hwenable is not None:
            E = self.exp.dereferencer.get_value(hwenable)
            next_val = f"{R} | {E}"
        else:
            next_val = "'1"

        return [
            f"field_combo.{field_path}.next = {next_val};",
            f"field_combo.{field_path}.load_next = '1;",
        ]


class HWClear(NextStateConditional):
    comment = "HW Clear"
    def is_match(self, field: 'FieldNode') -> bool:
        return bool(field.get_property('hwclr'))

    def get_predicate(self, field: 'FieldNode') -> str:
        prop = field.get_property('hwclr')
        if isinstance(prop, bool):
            identifier = self.exp.hwif.get_implied_prop_input_identifier(field, "hwclr")
        else:
            # signal or field
            identifier = self.exp.dereferencer.get_value(prop)
        return identifier

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        field_path = self.get_field_path(field)

        hwmask = field.get_property('hwmask')
        hwenable = field.get_property('hwenable')
        R = f"field_storage.{field_path}"
        if hwmask is not None:
            M = self.exp.dereferencer.get_value(hwmask)
            next_val = f"{R} & {M}"
        elif hwenable is not None:
            E = self.exp.dereferencer.get_value(hwenable)
            next_val = f"{R} & ~{E}"
        else:
            next_val = "'0"

        return [
            f"field_combo.{field_path}.next = {next_val};",
            f"field_combo.{field_path}.load_next = '1;",
        ]
