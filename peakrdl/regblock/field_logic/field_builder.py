from typing import TYPE_CHECKING
from collections import OrderedDict

from systemrdl.rdltypes import PrecedenceType

from .bases import AssignmentPrecedence, NextStateConditional
from . import sw_onread
from . import sw_onwrite

from ..struct_generator import RDLStructGenerator
from ..forloop_generator import RDLForLoopGenerator
from ..utils import get_indexed_path, get_always_ff_event
from ..signals import RDLSignal


if TYPE_CHECKING:
    from typing import Dict, List

    from systemrdl.node import FieldNode, AddrmapNode

    from ..exporter import RegblockExporter


class FieldBuilder:

    def __init__(self, exporter:'RegblockExporter'):
        self.exporter = exporter

        self._hw_conditionals = {} # type: Dict[int, List[NextStateConditional]]
        self._sw_conditionals = {} # type: Dict[int, List[NextStateConditional]]

        self.init_conditionals()

    @property
    def top_node(self) -> 'AddrmapNode':
        return self.exporter.top_node

    def add_hw_conditional(self, conditional: NextStateConditional, precedence: AssignmentPrecedence) -> None:
        # TODO: Add docstring!
        if precedence not in self._hw_conditionals:
            self._hw_conditionals[precedence] = []
        self._hw_conditionals[precedence].append(conditional)


    def add_sw_conditional(self, conditional: NextStateConditional, precedence: AssignmentPrecedence) -> None:
        # TODO: Add docstring!
        if precedence not in self._sw_conditionals:
            self._sw_conditionals[precedence] = []
        self._sw_conditionals[precedence].append(conditional)


    def init_conditionals(self) -> None:
        # TODO: Add docstring!

        # TODO: Add all the other things
        self.add_sw_conditional(sw_onread.ClearOnRead(self.exporter), AssignmentPrecedence.SW_ONREAD)
        self.add_sw_conditional(sw_onread.SetOnRead(self.exporter), AssignmentPrecedence.SW_ONREAD)

        self.add_hw_conditional(sw_onwrite.WriteOneSet(self.exporter), AssignmentPrecedence.SW_ONWRITE)
        self.add_hw_conditional(sw_onwrite.WriteOneClear(self.exporter), AssignmentPrecedence.SW_ONWRITE)
        self.add_hw_conditional(sw_onwrite.WriteOneToggle(self.exporter), AssignmentPrecedence.SW_ONWRITE)
        self.add_hw_conditional(sw_onwrite.WriteZeroSet(self.exporter), AssignmentPrecedence.SW_ONWRITE)
        self.add_hw_conditional(sw_onwrite.WriteZeroClear(self.exporter), AssignmentPrecedence.SW_ONWRITE)
        self.add_hw_conditional(sw_onwrite.WriteZeroToggle(self.exporter), AssignmentPrecedence.SW_ONWRITE)
        self.add_hw_conditional(sw_onwrite.WriteClear(self.exporter), AssignmentPrecedence.SW_ONWRITE)
        self.add_hw_conditional(sw_onwrite.WriteSet(self.exporter), AssignmentPrecedence.SW_ONWRITE)
        self.add_hw_conditional(sw_onwrite.Write(self.exporter), AssignmentPrecedence.SW_ONWRITE)



    def _get_X_conditionals(self, conditionals: 'Dict[int, List[NextStateConditional]]', field: 'FieldNode') -> 'List[NextStateConditional]':
        result = []
        precedences = sorted(conditionals.keys(), reverse=True)
        for precedence in precedences:
            for conditional in conditionals[precedence]:
                if conditional.is_match(field):
                    result.append(conditional)
        return result


    def get_conditionals(self, field: 'FieldNode') -> 'List[NextStateConditional]':
        # TODO: Add docstring! - list of NextStateConditional. Highest precedence comes first
        sw_precedence = (field.get_property('precedence') == PrecedenceType.sw)
        result = []

        if sw_precedence:
            result.extend(self._get_X_conditionals(self._sw_conditionals, field))

        result.extend(self._get_X_conditionals(self._hw_conditionals, field))

        if not sw_precedence:
            result.extend(self._get_X_conditionals(self._sw_conditionals, field))

        return result


class CombinationalStructGenerator(RDLStructGenerator):

    def __init__(self, field_builder: FieldBuilder):
        super().__init__()
        self.field_builder = field_builder


    def enter_Field(self, node: 'FieldNode') -> None:
        # If a field doesn't implement storage, it is not relevant here
        if not node.implements_storage:
            return

        # collect any extra combo signals that this field requires
        extra_combo_signals = OrderedDict()
        for conditional in self.field_builder.get_conditionals(node):
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
    def __init__(self, field_builder: FieldBuilder):
        super().__init__()
        self.field_builder = field_builder
        self.template = self.field_builder.exporter.jj_env.get_template(
            "field_logic/templates/field_storage.sv"
        )


    def enter_Field(self, node: 'FieldNode') -> None:
        # If a field doesn't implement storage, it is not relevant here
        if not node.implements_storage:
            return

        conditionals = self.field_builder.get_conditionals(node)
        extra_combo_signals = OrderedDict()
        for conditional in conditionals:
            for signal in conditional.get_extra_combo_signals(node):
                extra_combo_signals[signal.name] = signal

        reset_value = node.get_property("reset") or 0

        sig = node.get_property("resetsignal")
        if sig is not None:
            resetsignal = RDLSignal(sig)
        else:
            resetsignal = self.field_builder.exporter.default_resetsignal

        context = {
            'node': node,
            'reset': self.field_builder.exporter.dereferencer.get_value(reset_value),
            'field_path': get_indexed_path(self.field_builder.top_node, node),
            'extra_combo_signals': extra_combo_signals,
            'conditionals': conditionals,
            'resetsignal': resetsignal,
            'get_always_ff_event': get_always_ff_event,
            'has_value_output': self.field_builder.exporter.hwif.has_value_output,
            'get_output_identifier': self.field_builder.exporter.hwif.get_output_identifier,

        }
        self.add_content(self.template.render(context))
