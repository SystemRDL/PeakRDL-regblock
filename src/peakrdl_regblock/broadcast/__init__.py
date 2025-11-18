from typing import TYPE_CHECKING, Dict, List
from collections import defaultdict

from systemrdl.node import RegNode, RegfileNode, AddressableNode
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
                    # We can only safely OR this broadcaster if it targets ALL elements of the array
                    # Otherwise we'd incorrectly apply broadcasts to non-target elements

                    # Get the array base path (eg 'regblock.reg_array')
                    array_base_with_bracket = target_path.replace('[]', '[')  # 'regblock.reg_array['

                    # Check if this stored target is in the same array
                    if t_path.startswith(array_base_with_bracket):
                        # This broadcaster targets at least one element of this array
                        # But we need to check if it targets ALL elements

                        # Count how many elements of this array this broadcaster targets
                        array_element_count = 0
                        for target_in_list in targets:
                            if target_in_list.get_path().startswith(array_base_with_bracket):
                                array_element_count += 1

                        # Get the array size from the target node
                        if target.is_array and target.array_dimensions:
                            expected_count = 1
                            for dim in target.array_dimensions:
                                expected_count *= dim

                            # Only match if broadcaster targets ALL array elements
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

    def enter_Component(self, node: AddressableNode) -> None:


        # Only check broadcast_write property on Reg and Regfile nodes
        # (these are the valid_components for the UDP)
        if not isinstance(node, (RegNode, RegfileNode)):
            return

        # Check if this node has the broadcast_write property
        broadcast_targets = node.get_property('broadcast_write')

        if broadcast_targets is not None:
            # This is a broadcaster
            self.bl.broadcasters.append(node)

            # Expand targets (handle regfiles and arrays)
            expanded_targets = self._expand_targets(broadcast_targets)
            # Use path as key since RegNode is not hashable
            self.bl.broadcast_map[node.get_path()] = expanded_targets

            # Track all targets
            for target in expanded_targets:
                self.bl.targets.append(target)

    def _expand_targets(self, targets: any) -> List[RegNode]:
        """
        Expand broadcast targets into individual register nodes.

        Handles:
        - Single register/regfile reference
        - List of register/regfile references
        - Regfile references (expand to all child registers)
        - Array references (expand to all array elements)
        """
        # Normalize to list
        if not isinstance(targets, list):
            targets = [targets]

        expanded = []
        for target in targets:
            if isinstance(target, RegNode):
                # Single register - handle arrays
                if target.is_array:
                    # Expand to all array elements
                    expanded.extend(self._expand_array(target))
                else:
                    expanded.append(target)

            elif isinstance(target, RegfileNode):
                # Regfile - expand to all child registers
                if target.is_array:
                    # Expand regfile array to all elements
                    for regfile_elem in self._expand_array(target):
                        expanded.extend(self._expand_regfile(regfile_elem))
                else:
                    expanded.extend(self._expand_regfile(target))

        return expanded

    def _expand_array(self, node: AddressableNode) -> List[AddressableNode]:
        """
        For broadcast targets, we expect explicit array indexing in the RDL.
        Just return the node as-is since it's already the specific element.
        """
        # Simply return the node - RDL references should already be explicit
        return [node]

    def _expand_regfile(self, regfile: RegfileNode) -> List[RegNode]:
        """Expand a regfile to all its child registers"""
        registers = []

        def collect_regs(node):
            for child in node.children(skip_not_present=False):
                if isinstance(child, RegNode):
                    if child.is_array:
                        registers.extend(self._expand_array(child))
                    else:
                        registers.append(child)
                elif isinstance(child, RegfileNode):
                    # Recursively handle nested regfiles
                    if child.is_array:
                        for rf_elem in self._expand_array(child):
                            collect_regs(rf_elem)
                    else:
                        collect_regs(child)

        collect_regs(regfile)
        return registers
