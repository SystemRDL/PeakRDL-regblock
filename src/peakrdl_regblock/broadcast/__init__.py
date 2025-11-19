from typing import TYPE_CHECKING, Dict, List, Tuple, Any, Optional
from collections import defaultdict

from systemrdl.node import RegNode, RegfileNode, AddressableNode, Node
from systemrdl.walker import RDLListener, RDLWalker

if TYPE_CHECKING:
    from ..exporter import RegblockExporter


class BroadcastLogic:
    """
    Manages broadcast logic for registers and regfiles.

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

    def is_in_broadcast_scope(self, node: AddressableNode) -> bool:
        """
        Check if a node is within a broadcast scope.
        This includes:
        1. The node itself is a broadcaster
        2. The node is a child of a broadcaster (e.g. reg in a broadcast regfile)
        """
        curr: Optional[Node] = node
        while curr is not None:
            if isinstance(curr, AddressableNode) and self.is_broadcaster(curr):
                return True
            curr = curr.parent
        return False

    def is_target(self, node: RegNode) -> bool:
        """Check if a node is a broadcast target"""
        return node in self.targets

    def get_broadcasters_for_target(self, target: RegNode) -> List[AddressableNode]:
        """
        Get all broadcaster nodes that write to this target.
        """
        broadcasters: List[AddressableNode] = []

        # Calculate the total number of instances this target represents
        # (including its own array dimensions and any parent array dimensions)
        expected_count = 1
        curr: Optional[Node] = target
        while curr is not None:
            if isinstance(curr, AddressableNode) and curr.is_array:
                expected_count *= curr.n_elements
            curr = curr.parent

        for broadcaster_node, targets in self.broadcast_map:
            # 1. Exact match check
            if target in targets:
                broadcasters.append(broadcaster_node)
                continue

            # 2. Array iteration match check
            # If target is a canonical node inside an array loop, it won't be in the map.
            # But its unrolled instances (sharing the same underlying Component 'inst') might be.

            # Count how many targets share the same underlying component instance
            match_count = 0
            for t in targets:
                if t.inst == target.inst:
                    # If current_idx is None, this node represents the entire array (all elements)
                    if t.current_idx is None:
                        match_count += t.n_elements
                    else:
                        # Otherwise it represents a single element
                        match_count += 1

            if match_count == expected_count and expected_count > 0:
                broadcasters.append(broadcaster_node)

        return broadcasters


class BroadcastScanner(RDLListener):
    """Listener that scans the design to build the broadcast mapping"""

    def __init__(self, broadcast_logic: BroadcastLogic) -> None:
        self.bl = broadcast_logic
        # Stack of active broadcaster scopes: List[Tuple[BroadcasterNode, List[TargetNode]]]
        self.scope_stack: List[Tuple[AddressableNode, List[RegfileNode]]] = []

    def enter_Component(self, node: Node) -> None:

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
            broadcast_targets = node.get_property('broadcast')

            if broadcast_targets is not None:
                self.bl.broadcasters.append(node)

                if isinstance(node, RegfileNode):
                    # Structural Broadcast: Push to stack to handle children
                    # Filter targets to only RegfileNodes (validation ensures they are compatible)
                    rf_targets = [t for t in broadcast_targets if isinstance(t, RegfileNode)]
                    if rf_targets:
                        self.scope_stack.append((node, rf_targets))

                elif isinstance(node, RegNode):
                    # Direct Register Broadcast: Map immediately
                    for target in broadcast_targets:
                        if isinstance(target, RegNode):
                            self._add_broadcast_map(node, target)

    def exit_Component(self, node: Node) -> None:
        # Pop scope if we are exiting the current broadcaster scope
        if self.scope_stack and self.scope_stack[-1][0] == node:
            self.scope_stack.pop()

    def _add_broadcast_map(self, broadcaster: AddressableNode, target: RegNode) -> None:
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
