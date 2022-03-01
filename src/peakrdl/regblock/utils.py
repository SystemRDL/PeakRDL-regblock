import re
from typing import TYPE_CHECKING, Match

if TYPE_CHECKING:
    from systemrdl.node import Node, SignalNode
    from typing import Optional
    from .dereferencer import Dereferencer

def get_indexed_path(top_node: 'Node', target_node: 'Node') -> str:
    """
    TODO: Add words about indexing and why i'm doing this. Copy from logbook
    """
    path = target_node.get_rel_path(top_node, empty_array_suffix="[!]")
    # replace unknown indexes with incrementing iterators i0, i1, ...
    class repl:
        def __init__(self) -> None:
            self.i = 0
        def __call__(self, match: Match) -> str:
            s = f'i{self.i}'
            self.i += 1
            return s
    return re.sub(r'!', repl(), path)


def get_always_ff_event(dereferencer: 'Dereferencer', resetsignal: 'Optional[SignalNode]') -> str:
    if resetsignal is None:
        return "@(posedge clk)"
    if resetsignal.get_property('async') and resetsignal.get_property('activehigh'):
        return f"@(posedge clk or posedge {dereferencer.get_value(resetsignal)})"
    elif resetsignal.get_property('async') and not resetsignal.get_property('activehigh'):
        return f"@(posedge clk or negedge {dereferencer.get_value(resetsignal)})"
    return "@(posedge clk)"

def clog2(n: int) -> int:
    return (n-1).bit_length()

def is_pow2(x: int) -> bool:
    return (x > 0) and ((x & (x - 1)) == 0)
