from typing import Any

from systemrdl.component import Field, Signal
from systemrdl.node import Node, VectorNode
from systemrdl.udp import UDPDefinition


class FixedpointWidth(UDPDefinition):
    valid_components = {Field, Signal}
    valid_type = int

    def validate(self, node: "Node", value: Any) -> None:
        assert isinstance(node, VectorNode)

        intwidth = node.get_property("intwidth")
        fracwidth = node.get_property("fracwidth")
        assert intwidth is not None
        assert fracwidth is not None

        # ensure node width = fracwidth + intwidth
        if intwidth + fracwidth != node.width:
            self.msg.error(
                f"{type(node.inst).__name__.lower()} '{node.inst_name}' number of"
                f" integer bits ({intwidth}) plus number of fractional bits ({fracwidth})"
                f" must be equal to the width of the component ({node.width})."
            )


class IntWidth(FixedpointWidth):
    name = "intwidth"

    def get_unassigned_default(self, node: "Node") -> Any:
        # if 'fracwidth' is defined, 'intwidth' is inferred from the node width
        fracwidth = node.get_property("fracwidth", default=None)
        if fracwidth is not None:
            assert isinstance(node, VectorNode)
            return node.width - fracwidth
        else:
            # not a fixedpoint number
            return None


class FracWidth(FixedpointWidth):
    name = "fracwidth"

    def get_unassigned_default(self, node: "Node") -> Any:
        # if 'intwidth' is defined, 'fracwidth' is inferred from the node width
        intwidth = node.get_property("intwidth", default=None)
        if intwidth is not None:
            assert isinstance(node, VectorNode)
            return node.width - intwidth
        else:
            # not a fixedpoint number
            return None


class IsSigned(UDPDefinition):
    name = "is_signed"
    valid_components = {Field, Signal}
    valid_type = bool

    def get_unassigned_default(self, node: "Node") -> Any:
        intwidth = node.get_property("intwidth")
        if intwidth is not None:
            # it's a fixedpoint number, default to unsigned
            return False
        else:
            # not a fixedpoint number
            return None
