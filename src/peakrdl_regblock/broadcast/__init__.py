from typing import TYPE_CHECKING, Dict, List
from collections import defaultdict

from systemrdl.node import RegNode, RegfileNode, AddressableNode, Node
from systemrdl.walker import RDLListener, RDLWalker

if TYPE_CHECKING:
    from ..exporter import RegblockExporter


class BroadcastWriteLogic:
    """
    Manages broadcast write logic for registers and regfiles.

    A broadcaster register/regfile does not have hardware storage.
    Instead, writes to the broadcaster address generate write strobes
    for all target registers.
    """

    def __init__(self, exp: 'RegblockExporter') -> None:
        self.exp = exp

        # Maps broadcaster node to list of target nodes
        # List of tuples: (broadcaster_node, [target_nodes])
        self.broadcast_map: List[Tuple[AddressableNode, List[RegNode]]] = []

        # List of all broadcaster nodes (no hardware implementation)
        self.broadcasters: List[AddressableNode] = []

        # List of all target nodes (receive broadcast writes)
        self.targets: List[RegNode] = []

        # Scan the design to build the broadcast map
        self._scan_design()

    def _scan_design(self) -> None:
        """Scan the design to identify broadcasters and their targets"""
        listener = BroadcastScanner(self)
        RDLWalker(skip_not_present=False).walk(self.exp.ds.top_node, listener)

    def is_broadcaster(self, node: AddressableNode) -> bool:
        """Check if a node is a broadcaster"""
        return node in self.broadcasters

    def is_target(self, node: RegNode) -> bool:
        """Check if a node is a broadcast target"""
        return node in self.targets

    def get_broadcasters_for_target(self, target: RegNode) -> List[AddressableNode]:
        """
        Get all broadcaster nodes that write to this target.
        """
        broadcasters = []

        for broadcaster_node, targets in self.broadcast_map:
            # 1. Exact match check
            if target in targets:
                broadcasters.append(broadcaster_node)
                continue

            # 2. Array iteration match check
            # If target is a canonical node inside an array loop, it won't be in the map (which has unrolled nodes).
            # We need to check if the nodes in 'targets' correspond to this canonical 'target'.
            # We do this by checking if they share the same underlying Instance object and parent Instance.

            array_element_count = 0
            expected_count = 0

            # We only need to calculate expected_count if we find at least one potential match
            found_potential_match = False

            for t in targets:
                # Check if t is an instance of target
                # 1. Must share the same Instance object (same register definition/instance)
                # 2. Must share the same parent Instance object (same regfile/array instance)
                #    (This distinguishes between regfile_a.reg_a and regfile_b.reg_a)

                if t.inst == target.inst:
                    # Check parent equality (handle root case)
                    t_parent = t.parent
                    target_parent = target.parent

                    if t_parent is not None and target_parent is not None:
                        if t_parent.inst == target_parent.inst:
                            # Match found! 't' is an unrolled instance of 'target'
                            array_element_count += 1
                            found_potential_match = True
                    elif t_parent is None and target_parent is None:
                        # Both are root? Should have been caught by exact match, but ok.
                        array_element_count += 1
                        found_potential_match = True

            if found_potential_match:
                # Calculate expected count (size of the array)
                # The parent of the target should be the array
                parent = target.parent
                if parent and getattr(parent, 'is_array', False):
                    expected_count = 1
                    for dim in parent.array_dimensions:
                        expected_count *= dim

                # If target itself is an array (unlikely here as we usually target registers), handle that
                elif getattr(target, 'is_array', False):
                     expected_count = 1
                     for dim in target.array_dimensions:
                        expected_count *= dim
                else:
                    # If parent is not array and target is not array, expected is 1.
                    # But then exact match should have worked.
                    # Unless target is inside a generated loop for a non-array? (Unlikely)
                    expected_count = 1

                if array_element_count == expected_count and expected_count > 0:
                    broadcasters.append(broadcaster_node)

        return broadcasters


class BroadcastScanner(RDLListener):
    """Listener that scans the design to build the broadcast mapping"""

    def __init__(self, broadcast_logic: BroadcastWriteLogic) -> None:
        self.bl = broadcast_logic
        # Stack of active broadcaster scopes: List[Tuple[BroadcasterNode, List[TargetNode]]]
        self.scope_stack = []

    def enter_Component(self, node: AddressableNode) -> None:

        # 1. Check if we are inside an active broadcaster scope (Structural Broadcast)
        if self.scope_stack and isinstance(node, RegNode):
            broadcaster_scope, target_scopes = self.scope_stack[-1]

            # Calculate relative path from the broadcaster scope
            b_path = broadcaster_scope.get_path()
            node_path = node.get_path()

            if node_path.startswith(b_path + '.'):
                rel_path = node_path[len(b_path)+1:]

                # Map to each target scope
                for target_scope in target_scopes:
                    # Find corresponding node in target
                    target_reg = target_scope.find_by_path(rel_path)

                    if target_reg and isinstance(target_reg, RegNode):
                        self._add_broadcast_map(node, target_reg)

        # 2. Check if this node defines a new broadcast (is a Broadcaster)
        if isinstance(node, (RegNode, RegfileNode)):
            broadcast_targets = node.get_property('broadcast_write')

            if broadcast_targets is not None:
                self.bl.broadcasters.append(node)

                # Resolve targets (handle arrays)
                expanded_targets = self._expand_targets(broadcast_targets)

                if isinstance(node, RegfileNode):
                    # Structural Broadcast: Push to stack to handle children
                    # Filter targets to only RegfileNodes (validation ensures they are compatible)
                    rf_targets = [t for t in expanded_targets if isinstance(t, RegfileNode)]
                    if rf_targets:
                        self.scope_stack.append((node, rf_targets))

                elif isinstance(node, RegNode):
                    # Direct Register Broadcast: Map immediately
                    for target in expanded_targets:
                        if isinstance(target, RegNode):
                            self._add_broadcast_map(node, target)

    def exit_Component(self, node: AddressableNode) -> None:
        # Pop scope if we are exiting the current broadcaster scope
        if self.scope_stack and self.scope_stack[-1][0] == node:
            self.scope_stack.pop()

    def _expand_targets(self, targets: any) -> List[AddressableNode]:
        """
        Expand broadcast targets into a flat list of nodes.
        Handles:
        - Single reference
        - List of references
        - Array references (expand to all array elements)
        """
        # Normalize to list
        if not isinstance(targets, list):
            targets = [targets]

        final_targets = []
        for target in targets:
            if target.is_array:
                final_targets.extend(self._expand_array(target))
            else:
                final_targets.append(target)

        return final_targets

    def _add_broadcast_map(self, broadcaster: AddressableNode, target: RegNode):
        """Helper to add a broadcaster -> target mapping"""

        # Find existing entry for this broadcaster
        found = False
        for b_node, t_list in self.bl.broadcast_map:
            if b_node == broadcaster:
                if target not in t_list:
                    t_list.append(target)
                found = True
                break

        if not found:
            self.bl.broadcast_map.append((broadcaster, [target]))

        # Also track in global targets list
        if target not in self.bl.targets:
            self.bl.targets.append(target)

    def _expand_array(self, node: AddressableNode) -> List[AddressableNode]:
        """
        For broadcast targets, we expect explicit array indexing in the RDL.
        Just return the node as-is since it's already the specific element.
        """
        # Simply return the node - RDL references should already be explicit
        return [node]
