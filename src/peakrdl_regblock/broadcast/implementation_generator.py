from typing import TYPE_CHECKING, List, Optional

from systemrdl.node import AddressableNode, RegNode

from ..utils import get_indexed_path

if TYPE_CHECKING:
    from . import BroadcastWriteLogic


class BroadcastLogicGenerator:
    """Generates the broadcast write strobe logic"""

    def __init__(self, broadcast: 'BroadcastWriteLogic') -> None:
        self.broadcast = broadcast
        self.exp = broadcast.exp

    def get_content(self, top_node: AddressableNode) -> str:
        """Generate the broadcast logic SystemVerilog code"""
        if not self.broadcast.broadcast_map:
            return ""

        template = self.exp.jj_env.get_template("broadcast/template.sv")

        # Build a list of broadcaster info for the template
        # Each entry has the broadcaster path and node
        broadcaster_list = []
        for broadcaster_node, targets in self.broadcast.broadcast_map:
            broadcaster_list.append({
                'path': get_indexed_path(self.exp.ds.top_node, broadcaster_node),
                'node': broadcaster_node,
                'targets': targets
            })

        # Helper functions for template
        def get_path(node):
            return get_indexed_path(self.exp.ds.top_node, node)

        def get_signal_name(node, idx_list):
            """Generate unique signal name for broadcaster"""
            path = get_indexed_path(self.exp.ds.top_node, node)
            if idx_list:
                # Add array indexes
                for idx in idx_list:
                    path += f"_{idx}"
            return path.replace('.', '_').replace('[', '_').replace(']', '').replace('__', '_')

        def get_access_strobe(node, idx_list):
            """Get the access strobe for a broadcaster node"""
            if idx_list:
                # Get indexed node
                indexed_node = node.get_child_by_indexes(idx_list)
                return self.exp.dereferencer.get_access_strobe(indexed_node)
            else:
                return self.exp.dereferencer.get_access_strobe(node)

        def get_array_iterators(node):
            """Generate all index combinations for an array node"""
            if not node.is_array:
                return []

            indices = []

            def recurse(dims, current):
                if not dims:
                    indices.append(current[:])
                else:
                    for i in range(dims[0]):
                        current.append(i)
                        recurse(dims[1:], current)
                        current.pop()

            recurse(node.array_dimensions, [])
            return indices

        context = {
            'broadcaster_list': broadcaster_list,
            'dereferencer': self.exp.dereferencer,
            'get_path': get_path,
            'get_signal_name': get_signal_name,
            'get_access_strobe': get_access_strobe,
            'get_array_iterators': get_array_iterators,
        }

        return template.render(context)


    def get_broadcast_strobe(self, target: RegNode) -> Optional[str]:
        """
        Get the combined broadcast write strobe for a target register.
        Returns None if the target has no broadcasters.
        """
        broadcaster_nodes = self.broadcast.get_broadcasters_for_target(target)
        if not broadcaster_nodes:
            return None

        # Build OR expression of all broadcaster strobes
        strobe_terms = []
        for broadcaster_node in broadcaster_nodes:
            # Generate strobe signal name based on whether it's an array
            if broadcaster_node.is_array:
                # For arrays, we'd need to handle each element
                # For now, just generate non-array version
                # TODO: Handle array broadcasters properly
                signal_name = self._get_signal_name(broadcaster_node, None)
                strobe_terms.append(f"broadcast_wr_{signal_name}")
            else:
                signal_name = self._get_signal_name(broadcaster_node, None)
                strobe_terms.append(f"broadcast_wr_{signal_name}")

        if not strobe_terms:
            return None
        elif len(strobe_terms) == 1:
            return strobe_terms[0]
        else:
            return "(" + " || ".join(strobe_terms) + ")"

    def _get_signal_name(self, node: AddressableNode, idx_list: Optional[List[int]]) -> str:
        """Generate unique signal name for broadcaster"""
        path = get_indexed_path(self.exp.ds.top_node, node)
        if idx_list:
            for idx in idx_list:
                path += f"_{idx}"
        return path.replace('.', '_').replace('[', '_').replace(']', '').replace('__', '_')

    def _get_array_iterators(self, node: AddressableNode) -> List[List[int]]:
        """Generate all index combinations for an array node"""
        if not node.is_array:
            return []

        indices = []

        def recurse(dims, current):
            if not dims:
                indices.append(current[:])
            else:
                for i in range(dims[0]):
                    current.append(i)
                    recurse(dims[1:], current)
                    current.pop()

        recurse(node.array_dimensions, [])
        return indices
