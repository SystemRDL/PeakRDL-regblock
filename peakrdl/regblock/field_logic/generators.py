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
        self.template = self.field_logic.exp.jj_env.get_template(
            "field_logic/templates/field_storage.sv"
        )


    def enter_Field(self, node: 'FieldNode') -> None:
        # If a field doesn't implement storage, it is not relevant here
        if not node.implements_storage:
            return

        conditionals = self.field_logic.get_conditionals(node)
        extra_combo_signals = OrderedDict()
        for conditional in conditionals:
            for signal in conditional.get_extra_combo_signals(node):
                extra_combo_signals[signal.name] = signal

        sig = node.get_property("resetsignal")
        if sig is not None:
            resetsignal = RDLSignal(sig)
        else:
            resetsignal = self.field_logic.exp.default_resetsignal

        reset_value = node.get_property("reset")
        if reset_value is not None:
            reset_value_str = self.field_logic.exp.dereferencer.get_value(reset_value)
        else:
            # 5.9.1-g: If no reset value given, the field is not reset, even if it has a resetsignal.
            reset_value_str = None
            resetsignal = None

        context = {
            'node': node,
            'reset': reset_value_str,
            'field_path': get_indexed_path(self.field_logic.top_node, node),
            'extra_combo_signals': extra_combo_signals,
            'conditionals': conditionals,
            'resetsignal': resetsignal,
            'get_always_ff_event': get_always_ff_event,
            'has_value_output': self.field_logic.exp.hwif.has_value_output,
            'get_output_identifier': self.field_logic.exp.hwif.get_output_identifier,

        }
        self.add_content(self.template.render(context))
