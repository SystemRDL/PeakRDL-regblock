from typing import TYPE_CHECKING

from collections import OrderedDict

from ..struct_generator import RDLStructGenerator
from ..forloop_generator import RDLForLoopGenerator
from ..utils import get_indexed_path, get_always_ff_event
from ..signals import RDLSignal

if TYPE_CHECKING:
    from . import FieldLogic
    from systemrdl.node import FieldNode

class CombinationalStructGenerator(RDLStructGenerator):

    def __init__(self, field_logic: 'FieldLogic'):
        super().__init__()
        self.field_logic = field_logic


    def enter_Field(self, node: 'FieldNode') -> None:
        # If a field doesn't implement storage, it is not relevant here
        if not node.implements_storage:
            return

        # collect any extra combo signals that this field requires
        extra_combo_signals = OrderedDict()
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
        self.pop_struct()


class FieldStorageStructGenerator(RDLStructGenerator):

    def enter_Field(self, node: 'FieldNode') -> None:
        if node.implements_storage:
            self.add_member(node.inst_name, node.width)


class FieldLogicGenerator(RDLForLoopGenerator):
    i_type = "genvar"
    def __init__(self, field_logic: 'FieldLogic'):
        super().__init__()
        self.field_logic = field_logic
        self.exp = field_logic.exp
        self.field_storage_template = self.field_logic.exp.jj_env.get_template(
            "field_logic/templates/field_storage.sv"
        )


    def enter_Field(self, node: 'FieldNode') -> None:
        if node.implements_storage:
            self.generate_field_storage(node)

        self.assign_field_outputs(node)


    def generate_field_storage(self, node: 'FieldNode') -> None:
        conditionals = self.field_logic.get_conditionals(node)
        extra_combo_signals = OrderedDict()
        for conditional in conditionals:
            for signal in conditional.get_extra_combo_signals(node):
                extra_combo_signals[signal.name] = signal

        sig = node.get_property("resetsignal")
        if sig is not None:
            resetsignal = RDLSignal(sig)
        else:
            resetsignal = self.exp.default_resetsignal

        reset_value = node.get_property("reset")
        if reset_value is not None:
            reset_value_str = self.exp.dereferencer.get_value(reset_value)
        else:
            # 5.9.1-g: If no reset value given, the field is not reset, even if it has a resetsignal.
            reset_value_str = None
            resetsignal = None

        context = {
            'node': node,
            'reset': reset_value_str,
            'field_path': get_indexed_path(self.exp.top_node, node),
            'extra_combo_signals': extra_combo_signals,
            'conditionals': conditionals,
            'resetsignal': resetsignal,
            'get_always_ff_event': get_always_ff_event,
        }
        self.add_content(self.field_storage_template.render(context))


    def assign_field_outputs(self, node: 'FieldNode') -> None:
        field_path = get_indexed_path(self.exp.top_node, node)

        # Field value output
        if self.exp.hwif.has_value_output(node):
            output_identifier = self.exp.hwif.get_output_identifier(node)
            self.add_content(
                f"assign {output_identifier} = field_storage.{field_path};"
            )

        # Inferred logical reduction outputs
        if node.get_property("anded"):
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "anded")
            value = self.exp.dereferencer.get_field_propref_value(node, "anded")
            self.add_content(
                f"assign {output_identifier} = {value};"
            )
        if node.get_property("ored"):
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "ored")
            value = self.exp.dereferencer.get_field_propref_value(node, "ored")
            self.add_content(
                f"assign {output_identifier} = {value};"
            )
        if node.get_property("xored"):
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "xored")
            value = self.exp.dereferencer.get_field_propref_value(node, "xored")
            self.add_content(
                f"assign {output_identifier} = {value};"
            )

        if node.get_property("swmod"):
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "swmod")
            value = self.field_logic.get_swmod_identifier(node)
            self.add_content(
                f"assign {output_identifier} = {value};"
            )

        if node.get_property("swacc"):
            output_identifier = self.exp.hwif.get_implied_prop_output_identifier(node, "swacc")
            value = self.field_logic.get_swacc_identifier(node)
            self.add_content(
                f"assign {output_identifier} = {value};"
            )
