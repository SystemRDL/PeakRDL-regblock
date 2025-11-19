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

        # Maps broadcaster node PATH to list of target nodes
        # Using path strings as keys since RegNode is not hashable
        # After expansion, all targets are individual RegNodes
        self.broadcast_map: Dict[str, List[RegNode]] = {}

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

    def get_broadcasters_for_target(self, target: RegNode) -> List[str]:
        """
        Get all broadcaster paths that write to this target.

        For array iteration (target path has empty brackets []), only returns broadcasters
        that target ALL elements of the array, as we cannot conditionally OR subset
        broadcasts in the FOR loop.
        """
        broadcasters = []
        target_path = target.get_path()

        for broadcaster_path, targets in self.broadcast_map.items():
            # Compare by path since array elements may be different node objects
            for t in targets:
                t_path = t.get_path()

                # Handle two cases:
                # 1. Exact match: 'regblock.rega' == 'regblock.rega'
                # 2. Array iteration match: 'regblock.reg_array[]' matches only if broadcaster targets ALL elements
                is_match = False
                if t_path == target_path:
                    # Exact match
                    is_match = True
                elif '[]' in target_path:
                    # Target has empty brackets (array iteration variable in FOR loop)
                    # Example: 'regblock.regfile_array[].reg_a'

                    # Split path into prefix (before []) and suffix (after [])
                    prefix, suffix = target_path.split('[]', 1)

                    # Check if stored target matches pattern: prefix + [index] + suffix
                    if t_path.startswith(prefix + '[') and t_path.endswith(suffix):
                        # Extract the index part
                        # t_path = prefix + '[' + index + ']' + suffix
                        middle = t_path[len(prefix):-len(suffix) if suffix else None]

                        # Check if middle is '[<digits>]'
                        if middle.startswith('[') and middle.endswith(']') and middle[1:-1].isdigit():
                            # This is a match for a specific element of this array structure

                            # Now check if we are broadcasting to ALL elements of this array
                            # We need to count how many elements of this array structure are targeted

                            array_element_count = 0
                            for target_in_list in targets:
                                t_list_path = target_in_list.get_path()
                                if (t_list_path.startswith(prefix + '[') and
                                    t_list_path.endswith(suffix) and
                                    t_list_path[len(prefix):-len(suffix) if suffix else None].startswith('[') and
                                    t_list_path[len(prefix):-len(suffix) if suffix else None].endswith(']')):
                                    array_element_count += 1

                            # Get the array size from the target node
                            # Let's find the array node by path
                            array_path = prefix.rstrip('.')

                            # Try to find relative to top node if full path fails
                            top_node = self.exp.ds.top_node
                            top_path = top_node.get_path()

                            array_node = top_node.find_by_path(array_path)

                            if array_node is None and array_path.startswith(top_path + '.'):
                                # Try relative path
                                rel_path = array_path[len(top_path)+1:]
                                array_node = top_node.find_by_path(rel_path)

                            expected_count = 1
                            if array_node and getattr(array_node, 'is_array', False):
                                for dim in array_node.array_dimensions:
                                    expected_count *= dim

                            if array_element_count == expected_count:
                                is_match = True

                if is_match:
                    broadcasters.append(broadcaster_path)
                    break
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
        b_path = broadcaster.get_path()
        if b_path not in self.bl.broadcast_map:
            self.bl.broadcast_map[b_path] = []

        # Avoid duplicates
        if target not in self.bl.broadcast_map[b_path]:
            self.bl.broadcast_map[b_path].append(target)
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
