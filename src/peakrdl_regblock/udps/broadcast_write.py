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
        # Allow Reg -> Reg (same type)
        # Allow Regfile -> Regfile (structural broadcast)
        # Do NOT allow Reg -> Regfile (ambiguous - broadcast to all? user says no)

        broadcaster_type = type(broadcaster.inst)
        target_type = type(target.inst)

        is_compatible = False
        if broadcaster_type == target_type:
            # For regfiles, we should ideally check if they are the same definition
            # or at least structurally compatible.
            # For now, strict type equality of the component class is a start,
            # but we should probably check if they are instances of the same RDL type.
            # SystemRDL's 'type_name' or similar might be useful, but 'inst.type_name' isn't always available.
            # Let's rely on the fact that if they are both Regfiles, we will try to match children.
            # If children don't match, the expansion logic will just find nothing (or we can add a check there).
            is_compatible = True

        if not is_compatible:
            self.msg.error(
                f"Incompatible broadcast types. "
                f"Broadcaster '{broadcaster_type.__name__.lower()}' cannot target '{target_type.__name__.lower()}'. "
                f"Supported: reg->reg, regfile->regfile (same structure)",
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
