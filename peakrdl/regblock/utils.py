import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from systemrdl.node import Node
    from .signals import SignalBase
    from typing import Optional

def get_indexed_path(top_node: 'Node', target_node: 'Node') -> str:
    """
    TODO: Add words about indexing and why i'm doing this. Copy from logbook
    """
    path = target_node.get_rel_path(top_node, empty_array_suffix="[!]")
    # replace unknown indexes with incrementing iterators i0, i1, ...
    class repl:
        def __init__(self):
            self.i = 0
        def __call__(self, match):
            s = f'i{self.i}'
            self.i += 1
            return s
    return re.sub(r'!', repl(), path)


def get_always_ff_event(resetsignal: 'Optional[SignalBase]') -> str:
    if resetsignal is None:
        return "@(posedge clk)"
    if resetsignal.is_async and resetsignal.is_activehigh:
        return f"@(posedge clk or posedge {resetsignal.identifier})"
    elif resetsignal.is_async and not resetsignal.is_activehigh:
        return f"@(posedge clk or negedge {resetsignal.identifier})"
    return "@(posedge clk)"

def clog2(n: int) -> int:
    return n.bit_length() - 1
