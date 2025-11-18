from typing import Any, List

from systemrdl.udp import UDPDefinition
from systemrdl.component import Reg, Regfile
from systemrdl.rdltypes.references import RefType
from systemrdl.rdltypes.array import ArrayedType
from systemrdl.rdltypes import NoValue
from systemrdl.node import Node, RegNode, RegfileNode


class BroadcastWrite(UDPDefinition):
    name = "broadcast_write"
    valid_components = {Reg, Regfile}
    valid_type = ArrayedType(RefType)

    def validate(self, node: Node, value: Any) -> None:
        if value is NoValue:
            self.msg.error(
                "The 'broadcast_write' property requires a value assignment",
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
        if type(broadcaster.inst) != type(target.inst):
            self.msg.error(
                f"Broadcaster and target must be the same component type. "
                f"Broadcaster is '{type(broadcaster.inst).__name__.lower()}' but target is '{type(target.inst).__name__.lower()}'",
                self.get_src_ref(broadcaster)
            )
            return

        # For registers, check that they have the same regwidth
        if isinstance(broadcaster, RegNode) and isinstance(target, RegNode):
            broadcaster_width = broadcaster.get_property('regwidth')
            target_width = target.get_property('regwidth')
            if broadcaster_width != target_width:
                self.msg.error(
                    f"Broadcaster register width ({broadcaster_width}) must match target register width ({target_width})",
                    self.get_src_ref(broadcaster)
                )

        # Check internal/external boundary
        # A broadcaster and its targets must both be internal, or both be external
        if broadcaster.external != target.external:
            self.msg.error(
                f"Broadcaster and target must not cross internal/external boundary. "
                f"Broadcaster is {'external' if broadcaster.external else 'internal'}, "
                f"target is {'external' if target.external else 'internal'}",
                self.get_src_ref(broadcaster)
            )

        # Check that target is writable
        if isinstance(target, RegNode):
            if not target.has_sw_writable:
                self.msg.error(
                    f"Broadcast target register '{target.inst_name}' has no software-writable fields",
                    self.get_src_ref(broadcaster)
                )

        # Check for circular references (target is also a broadcaster)
        if target.get_property('broadcast_write') is not None:
            self.msg.error(
                f"Broadcast target '{target.inst_name}' cannot itself be a broadcaster (circular reference)",
                self.get_src_ref(broadcaster)
            )

    def get_unassigned_default(self, node: Node) -> Any:
        return None
