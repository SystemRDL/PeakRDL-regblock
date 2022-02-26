from typing import TYPE_CHECKING, List

from collections import OrderedDict

from ..struct_generator import RDLStructGenerator
from ..forloop_generator import RDLForLoopGenerator
from ..utils import get_always_ff_event

if TYPE_CHECKING:
    from . import FieldLogic
    from systemrdl.node import FieldNode, RegNode
    from .bases import SVLogic

class CombinationalStructGenerator(RDLStructGenerator):

    def __init__(self, field_logic: 'FieldLogic'):
        super().__init__()
        self.field_logic = field_logic


    def enter_Field(self, node: 'FieldNode') -> None:
        # If a field doesn't implement storage, it is not relevant here
        if not node.implements_storage:
            return

        # collect any extra combo signals that this field requires
        extra_combo_signals = OrderedDict() # type: OrderedDict[str, SVLogic]
        for conditional in self.field_logic.get_conditionals(node):
            for signal in conditional.get_extra_combo_signals(node):
                if signal.name in extra_combo_signals:
                    # Assert that subsequent declarations of the same signal
                    # are identical
                    assert signal == extra_combo_signals[signal.name]
                else:
                    extra_combo_signals[signal.name] = signal

        self.push_struct(node.inst_name)
        self.add_member("next", node.width)
        self.add_member("load_next")
        for signal in extra_combo_signals.values():
            self.add_member(signal.name, signal.width)
        if node.is_up_counter:
            self.add_up_counter_members(node)
        if node.is_down_counter:
            self.add_down_counter_members(node)
        self.pop_struct()

    def add_up_counter_members(self, node: 'FieldNode') -> None:
        self.add_member('incrthreshold')
        if self.field_logic.counter_incrsaturates(node):
            self.add_member('incrsaturate')
        else:
            self.add_member('overflow')

    def add_down_counter_members(self, node: 'FieldNode') -> None:
        self.add_member('decrthreshold')
        if self.field_logic.counter_decrsaturates(node):
            self.add_member('decrsaturate')
        else:
            self.add_member('underflow')


class FieldStorageStructGenerator(RDLStructGenerator):

    def __init__(self, field_logic: 'FieldLogic') -> None:
        super().__init__()
        self.field_logic = field_logic

    def enter_Field(self, node: 'FieldNode') -> None:
        self.push_struct(node.inst_name)

        if node.implements_storage:
            self.add_member("value", node.width)

        if self.field_logic.has_next_q(node):
            self.add_member("next_q", node.width)

        self.pop_struct()


class FieldLogicGenerator(RDLForLoopGenerator):
    i_type = "genvar"
    def __init__(self, field_logic: 'FieldLogic') -> None:
        super().__init__()
        self.field_logic = field_logic
        self.exp = field_logic.exp
        self.field_storage_template = self.field_logic.exp.jj_env.get_template(
            "field_logic/templates/field_storage.sv"
        )
        self.intr_fields = [] # type: List[FieldNode]
        self.halt_fields = [] # type: List[FieldNode]


    def enter_Reg(self, node: 'RegNode') -> None:
        self.intr_fields = []
        self.halt_fields = []


    def enter_Field(self, node: 'FieldNode') -> None:
        if node.implements_storage:
            self.generate_field_storage(node)

        self.assign_field_outputs(node)

        if node.get_property('intr'):
            self.intr_fields.append(node)
            if node.get_property('haltenable') or node.get_property('haltmask'):
                self.halt_fields.append(node)


    def exit_Reg(self, node: 'RegNode') -> None:
        # Assign register's intr output
        if self.intr_fields:
            strs = []
            for field in self.intr_fields:
                enable = field.get_property('enable')
                mask = field.get_property('mask')
                F = self.exp.dereferencer.get_value(field)
                if enable:
                    E = self.exp.dereferencer.get_value(enable)
                    s = f"|({F} & {E})"
                elif mask:
                    M = self.exp.dereferencer.get_value(mask)
                    s = f"|({F} & ~{M})"
                else:
                    s = f"|{F}"
                strs.append(s)

            self.add_content(
                f"assign {self.exp.hwif.get_implied_prop_output_identifier(node, 'intr')} ="
            )
            self.add_content(
                "    "
                + "\n    || ".join(strs)
                + ";"
            )

        # Assign register's halt output
        if self.halt_fields:
            strs = []
            for field in self.halt_fields:
                enable = field.get_property('haltenable')
                mask = field.get_property('haltmask')
                F = self.exp.dereferencer.get_value(field)
                if enable:
                    E = self.exp.dereferencer.get_value(enable)
                    s = f"|({F} & {E})"
                elif mask:
                    M = self.exp.dereferencer.get_value(mask)
                    s = f"|({F} & ~{M})"
                else:
                    s = f"|{F}"
                strs.append(s)

            self.add_content(
                f"assign {self.exp.hwif.get_implied_prop_output_identifier(node, 'halt')} ="
            )
            self.add_content(
                "    "
                + "\n    || ".join(strs)
                + ";"
            )


    def generate_field_storage(self, node: 'FieldNode') -> None:
        conditionals = self.field_logic.get_conditionals(node)
        extra_combo_signals = OrderedDict()
        for conditional in conditionals:
            for signal in conditional.get_extra_combo_signals(node):
                extra_combo_signals[signal.name] = signal

        resetsignal = node.get_property('resetsignal')

        reset_value = node.get_property('reset')
        if reset_value is not None:
            reset_value_str = self.exp.dereferencer.get_value(reset_value)
        else:
            # 5.9.1-g: If no reset value given, the field is not reset, even if it has a resetsignal.
            reset_value_str = None
            resetsignal = None

        context = {
            'node': node,
            'reset': reset_value_str,
            'field_logic': self.field_logic,
            'extra_combo_signals': extra_combo_signals,
            'conditionals': conditionals,
            'resetsignal': resetsignal,
            'get_always_ff_event': lambda resetsignal : get_always_ff_event(self.exp.dereferencer, resetsignal),
            'get_value': self.exp.dereferencer.get_value,
            'get_resetsignal': self.exp.dereferencer.get_resetsignal,
            'get_input_identifier': self.exp.hwif.get_input_identifier,
        }
        self.add_content(self.field_storage_template.render(context))


    def assign_field_outputs(self, node: 'FieldNode') -> None:
        # Field value output
        if self.exp.hwif.has_value_output(node):
            output_identifier = self.exp.hwif.get_output_identifier(node)
            value = self.exp.dereferencer.get_value(node)
            self.add_content(
                f"assign {output_identifier} = {value};"
            )

        # Inferred logical reduction outputs
        if node.get_property('anded'):
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "anded")
            value = self.exp.dereferencer.get_field_propref_value(node, "anded")
            self.add_content(
                f"assign {output_identifier} = {value};"
            )
        if node.get_property('ored'):
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "ored")
            value = self.exp.dereferencer.get_field_propref_value(node, "ored")
            self.add_content(
                f"assign {output_identifier} = {value};"
            )
        if node.get_property('xored'):
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "xored")
            value = self.exp.dereferencer.get_field_propref_value(node, "xored")
            self.add_content(
                f"assign {output_identifier} = {value};"
            )

        if node.get_property('swmod'):
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "swmod")
            value = self.field_logic.get_swmod_identifier(node)
            self.add_content(
                f"assign {output_identifier} = {value};"
            )

        if node.get_property('swacc'):
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "swacc")
            value = self.field_logic.get_swacc_identifier(node)
            self.add_content(
                f"assign {output_identifier} = {value};"
            )

        if node.get_property('incrthreshold') is not False: # (explicitly not False. Not 0)
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "incrthreshold")
            value = self.field_logic.get_field_combo_identifier(node, 'incrthreshold')
            self.add_content(
                f"assign {output_identifier} = {value};"
            )
        if node.get_property('decrthreshold') is not False: # (explicitly not False. Not 0)
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "decrthreshold")
            value = self.field_logic.get_field_combo_identifier(node, 'decrthreshold')
            self.add_content(
                f"assign {output_identifier} = {value};"
            )

        if node.get_property('overflow'):
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "overflow")
            value = self.field_logic.get_field_combo_identifier(node, 'overflow')
            self.add_content(
                f"assign {output_identifier} = {value};"
            )
        if node.get_property('underflow'):
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "underflow")
            value = self.field_logic.get_field_combo_identifier(node, 'underflow')
            self.add_content(
                f"assign {output_identifier} = {value};"
            )
