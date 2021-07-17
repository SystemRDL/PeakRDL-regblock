from typing import TYPE_CHECKING, Union
from systemrdl.node import AddrmapNode, FieldNode, SignalNode, RegNode
from systemrdl.rdltypes import PropertyReference

if TYPE_CHECKING:
    from .exporter import RegblockExporter
    from .hwif import Hwif
    from .field_logic import FieldLogic
    from .addr_decode import AddressDecode

class Dereferencer:
    """
    This class provides an interface to convert conceptual SystemRDL references
    into Verilog identifiers
    """
    def __init__(self, exporter:'RegblockExporter'):
        self.exporter = exporter

    @property
    def hwif(self) -> 'Hwif':
        return self.exporter.hwif

    @property
    def address_decode(self) -> 'AddressDecode':
        return self.exporter.address_decode

    @property
    def field_logic(self) -> 'FieldLogic':
        return self.exporter.field_logic

    @property
    def top_node(self) -> AddrmapNode:
        return self.exporter.top_node

    def get_value(self, obj: Union[int, FieldNode, SignalNode, PropertyReference]) -> str:
        """
        Returns the Verilog string that represents the readable value associated
        with the object.

        If given a simple scalar value, then the corresponding Verilog literal is returned.

        If obj references a structural systemrdl object, then the corresponding Verilog
        expression is returned that represents its value.
        """
        if isinstance(obj, int):
            # Is a simple scalar value
            return f"'h{obj:x}"

        if isinstance(obj, FieldNode):
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

        if isinstance(obj, SignalNode):
            # Signals are always inputs from the hwif
            return self.hwif.get_input_identifier(obj)

        if isinstance(obj, PropertyReference):

            # Value reduction properties.
            # Wrap with the appropriate Verilog reduction operator
            val = self.get_value(obj.node)
            if obj.name == "anded":
                return f"&({val})"
            elif obj.name == "ored":
                return f"|({val})"
            elif obj.name == "xored":
                return f"^({val})"

            # references that directly access a property value
            if obj.name in {
                'decrvalue',
                'enable',
                'haltenable',
                'haltmask',
                'hwenable',
                'hwmask',
                'incrvalue',
                'mask',
                'reset',
                'resetsignal',
            }:
                return self.get_value(obj.node.get_property(obj.name))
            elif obj.name in {'incr', 'decr'}:
                prop_value = obj.node.get_property(obj.name)
                if prop_value is None:
                    # unset by the user, points to the implied internal signal
                    return self.field_logic.get_counter_control_identifier(obj)
                else:
                    return self.get_value(prop_value)
            elif obj.name == "next":
                prop_value = obj.node.get_property(obj.name)
                if prop_value is None:
                    # unset by the user, points to the implied internal signal
                    return self.field_logic.get_field_next_identifier(obj.node)
                else:
                    return self.get_value(prop_value)

            # References to another component value, or an implied input
            if obj.name in {'hwclr', 'hwset'}:
                prop_value = obj.node.get_property(obj.name)
                if prop_value is True:
                    # Points to inferred hwif input
                    return self.hwif.get_input_identifier(obj)
                elif prop_value is False:
                    # This should never happen, as this is checked by the compiler's validator
                    raise RuntimeError
                else:
                    return self.get_value(prop_value)

            # References to another component value, or an implied input
            # May have a complementary partner property
            complementary_pairs = {
                "we": "wel",
                "wel": "we",
                "swwe": "swwel",
                "swwel": "swwe",
            }
            if obj.name in complementary_pairs:
                prop_value = obj.node.get_property(obj.name)
                if prop_value is True:
                    # Points to inferred hwif input
                    return self.hwif.get_input_identifier(obj)
                elif prop_value is False:
                    # Try complementary property
                    prop_value = obj.node.get_property(complementary_pairs[obj.name])
                    if prop_value is True:
                        # Points to inferred hwif input
                        return f"!({self.hwif.get_input_identifier(obj)})"
                    elif prop_value is False:
                        # This should never happen, as this is checked by the compiler's validator
                        raise RuntimeError
                    else:
                        return f"!({self.get_value(prop_value)})"
                else:
                    return self.get_value(prop_value)

            """
            TODO:
            Resolves to an internal signal used in the field's logic
                decrsaturate
                decrthreshold
                halt
                incrsaturate
                incrthreshold
                intr
                overflow
                saturate
                swacc
                swmod
                threshold
            """

        raise RuntimeError("Unhandled reference to: %s", obj)



    def get_access_strobe(self, obj: Union[RegNode, FieldNode]) -> str:
        """
        Returns the Verilog string that represents the register's access strobe
        """
        return self.address_decode.get_access_strobe(obj)
