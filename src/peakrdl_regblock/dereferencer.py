from typing import TYPE_CHECKING, Union, Optional
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
    def __init__(self, exp:'RegblockExporter'):
        self.exp = exp

    @property
    def hwif(self) -> 'Hwif':
        return self.exp.hwif

    @property
    def address_decode(self) -> 'AddressDecode':
        return self.exp.address_decode

    @property
    def field_logic(self) -> 'FieldLogic':
        return self.exp.field_logic

    @property
    def top_node(self) -> AddrmapNode:
        return self.exp.top_node

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
                return self.get_value(reset_value)
            else:
                # No reset value defined!
                obj.env.msg.warning(
                    f"Field '{obj.inst_name}' is a constant but does not have a known value (missing reset). Assigning it a value of X.",
                    obj.inst.inst_src_ref
                )
                return "'X"

        if isinstance(obj, SignalNode):
            # Signals are always inputs from the hwif
            return self.hwif.get_input_identifier(obj)

        if isinstance(obj, PropertyReference):
            if isinstance(obj.node, FieldNode):
                return self.get_field_propref_value(obj.node, obj.name)
            elif isinstance(obj.node, RegNode):
                return self.get_reg_propref_value(obj.node, obj.name)
            else:
                raise RuntimeError

        raise RuntimeError(f"Unhandled reference to: {obj}")


    def get_field_propref_value(self, field: FieldNode, prop_name: str) -> str:
        # Value reduction properties.
        # Wrap with the appropriate Verilog reduction operator
        if prop_name == "anded":
            val = self.get_value(field)
            return f"&({val})"
        elif prop_name == "ored":
            val = self.get_value(field)
            return f"|({val})"
        elif prop_name == "xored":
            val = self.get_value(field)
            return f"^({val})"

        # references that directly access a property value
        if prop_name in {
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
            return self.get_value(field.get_property(prop_name))

        # Field Next
        if prop_name == "next":
            prop_value = field.get_property(prop_name)
            if prop_value is None:
                # unset by the user, points to the implied internal signal
                return self.field_logic.get_field_combo_identifier(field, "next")
            else:
                return self.get_value(prop_value)

        # References to another component value, or an implied input
        if prop_name in {'hwclr', 'hwset'}:
            prop_value = field.get_property(prop_name)
            if prop_value is True:
                # Points to inferred hwif input
                return self.hwif.get_implied_prop_input_identifier(field, prop_name)
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
        if prop_name in complementary_pairs:
            prop_value = field.get_property(prop_name)
            if prop_value is True:
                # Points to inferred hwif input
                return self.hwif.get_implied_prop_input_identifier(field, prop_name)
            elif prop_value is False:
                # Try complementary property
                prop_value = field.get_property(complementary_pairs[prop_name])
                if prop_value is True:
                    # Points to inferred hwif input
                    return f"!({self.hwif.get_implied_prop_input_identifier(field, complementary_pairs[prop_name])})"
                elif prop_value is False:
                    # This should never happen, as this is checked by the compiler's validator
                    raise RuntimeError
                else:
                    return f"!({self.get_value(prop_value)})"
            else:
                return self.get_value(prop_value)

        if prop_name == "swacc":
            return self.field_logic.get_swacc_identifier(field)
        if prop_name == "swmod":
            return self.field_logic.get_swmod_identifier(field)
        if prop_name == "rd_swacc":
            return self.field_logic.get_rd_swacc_identifier(field)
        if prop_name == "wr_swacc":
            return self.field_logic.get_wr_swacc_identifier(field)


        # translate aliases
        aliases = {
            "saturate": "incrsaturate",
            "threshold": "incrthreshold",
        }
        prop_name = aliases.get(prop_name, prop_name)

        # Counter properties
        if prop_name == 'incr':
            return self.field_logic.get_counter_incr_strobe(field)
        if prop_name == 'decr':
            return self.field_logic.get_counter_decr_strobe(field)

        if prop_name in {
            'decrsaturate',
            'decrthreshold',
            'incrsaturate',
            'incrthreshold',
            'overflow',
            'underflow',
        }:
            return self.field_logic.get_field_combo_identifier(field, prop_name)

        raise RuntimeError(f"Unhandled reference to: {field}->{prop_name}")


    def get_reg_propref_value(self, reg: RegNode, prop_name: str) -> str:
        if prop_name in {'halt', 'intr'}:
            return self.hwif.get_implied_prop_output_identifier(reg, prop_name)
        raise NotImplementedError


    def get_access_strobe(self, obj: Union[RegNode, FieldNode], reduce_substrobes: bool=True) -> str:
        """
        Returns the Verilog string that represents the register's access strobe
        """
        return self.address_decode.get_access_strobe(obj, reduce_substrobes)

    def get_resetsignal(self, obj: Optional[SignalNode]) -> str:
        """
        Returns a normalized active-high reset signal
        """
        if isinstance(obj, SignalNode):
            s = self.get_value(obj)
            if obj.get_property('activehigh'):
                return s
            else:
                return f"~{s}"

        # default reset signal
        return "rst"
