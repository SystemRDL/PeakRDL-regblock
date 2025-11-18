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
        """Get all broadcaster paths that write to this target"""
        broadcasters = []
        for broadcaster_path, targets in self.broadcast_map.items():
            if target in targets:
                broadcasters.append(broadcaster_path)
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
        """Recursively expand an array node to all its elements"""
        result = []

        def recurse(n, indexes):
            if len(indexes) == len(n.array_dimensions):
                # Reached leaf - get indexed node
                result.append(n.get_child_by_indexes(indexes))
            else:
                # Recurse through this dimension
                dim_size = n.array_dimensions[len(indexes)]
                for i in range(dim_size):
                    recurse(n, indexes + [i])

        recurse(node, [])
        return result

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
