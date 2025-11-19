from typing import Any

from systemrdl.udp import UDPDefinition
from systemrdl.component import Reg, Regfile
from systemrdl.rdltypes.references import RefType
from systemrdl.rdltypes.array import ArrayedType
from systemrdl.rdltypes import NoValue
from systemrdl.node import Node, RegNode, RegfileNode


class Broadcast(UDPDefinition):
    name = "broadcast"
    valid_components = {Reg, Regfile}
    valid_type = ArrayedType(RefType)

    def validate(self, node: Node, value: Any) -> None:
        if value is NoValue:
            self.msg.error(
                "The 'broadcast' property requires a target assignment",
                self.get_src_ref(node)
            )
            return

        # Convert single reference to list for uniform handling
        if not isinstance(value, list):
            targets = [value]
        else:
            targets = value

        if not targets:
            self.msg.error(
                "The 'broadcast_write' property must reference at least one target",
                self.get_src_ref(node)
            )
            return

        # Validate each target
        for target in targets:
            self._validate_target(node, target)

    def _validate_target(self, broadcaster: Node, target: Node) -> None:
        """Validate a single broadcast target"""

        # Check that target is a Reg or Regfile
        if not isinstance(target, (RegNode, RegfileNode)):
            self.msg.error(
                f"Broadcast target must be a register or regfile, not '{type(target.inst).__name__.lower()}'",
                self.get_src_ref(broadcaster)
            )
            return

        # Check type compatibility
        # TODO: How to check identity more thoroughly?
        broadcaster_type = type(broadcaster.inst)
        target_type = type(target.inst)

        if broadcaster_type != target_type:
            self.msg.error(
                f"Incompatible broadcast types. "
                f"Broadcaster '{broadcaster_type.__name__.lower()}' cannot target '{target_type.__name__.lower()}'. "
                f"Supported: reg->reg, regfile->regfile (same structure)",
                self.get_src_ref(broadcaster)
            )
            return

        # Check internal/external boundary
        # A broadcaster and its targets must both be internal, or both be external
        if broadcaster.external != target.external:
            self.msg.error(
                f"Broadcaster and target must not cross internal/external boundary. "
                f"Broadcaster is {'external' if broadcaster.external else 'internal'}, "
                f"target is {'external' if target.external else 'internal'}",
                self.get_src_ref(broadcaster)
            )

        # Check for circular references (target is also a broadcaster)
        if target.get_property('broadcast') is not None:
            self.msg.error(
                f"Broadcast target '{target.inst_name}' cannot also be a broadcaster",
                self.get_src_ref(broadcaster)
            )

    def get_unassigned_default(self, node: Node) -> Any:
        return None
