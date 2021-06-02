from typing import TYPE_CHECKING, Union
from systemrdl.node import Node, FieldNode, SignalNode, RegNode
from systemrdl.rdltypes import PropertyReference

if TYPE_CHECKING:
    from .exporter import RegblockExporter
    from .hwif.base import HwifBase
    from .field_logic import FieldLogic

class Dereferencer:
    """
    This class provides an interface to convert conceptual SystemRDL references
    into Verilog identifiers
    """
    def __init__(self, exporter:'RegblockExporter', hwif:'HwifBase', field_logic: "FieldLogic", top_node:Node):
        self.exporter = exporter
        self.hwif = hwif
        self.field_logic = field_logic
        self.top_node = top_node

    def get_value(self, obj: Union[int, FieldNode, SignalNode, PropertyReference]) -> str:
        """
        Returns the Verilog string that represents the value associated with the object.

        If given a simple scalar value, then the corresponding Verilog literal is returned.

        If obj references a structural systemrdl object, then the corresponding Verilog
        expression is returned that represents its value.
        """
        if isinstance(obj, int):
            # Is a simple scalar value
            return f"'h{obj:x}"

        elif isinstance(obj, FieldNode):
            if obj.implements_storage:
                return self.field_logic.get_storage_identifier(obj)

            if self.hwif.has_value_input(obj):
                return self.hwif.get_input_identifier(obj)

            # Field does not have a storage element, nor does it have a HW input
            # must be a constant value as defined by its reset value
            reset_value = obj.get_property('reset')
            if reset_value is not None:
                return f"'h{reset_value:x}"
            else:
                # No reset value defined!
                # Fall back to a value of 0
                return "'h0"

        elif isinstance(obj, SignalNode):
            # Signals are always inputs from the hwif
            return self.hwif.get_input_identifier(obj)

        elif isinstance(obj, PropertyReference):
            # TODO: Table G1 describes other possible ref targets

            # Value reduction properties
            val = self.get_value(obj.node)
            if obj.name == "anded":
                return f"&({val})"
            elif obj.name == "ored":
                return f"|({val})"
            elif obj.name == "xored":
                return f"^({val})"
            else:
                raise RuntimeError

        else:
            raise RuntimeError

    def get_access_strobe(self, reg: RegNode) -> str:
        """
        Returns the Verilog string that represents the register's access strobe
        """
        # TODO: Implement me
        raise NotImplementedError
