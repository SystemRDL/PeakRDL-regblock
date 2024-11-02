import re
from typing import Match, Union

from systemrdl.rdltypes.references import PropertyReference
from systemrdl.node import Node, AddrmapNode

from .identifier_filter import kw_filter as kwf
from .vhdl_int import VhdlInt

def get_indexed_path(top_node: Node, target_node: Node) -> str:
    """
    TODO: Add words about indexing and why i'm doing this. Copy from logbook
    """
    path = target_node.get_rel_path(top_node, empty_array_suffix="(!)")

    # replace unknown indexes with incrementing iterators i0, i1, ...
    class ReplaceUnknown:
        def __init__(self) -> None:
            self.i = 0
        def __call__(self, match: Match) -> str:
            s = f'i{self.i}'
            self.i += 1
            return s
    path = re.sub(r'!', ReplaceUnknown(), path)
    # change multidimensonal indices from (x)(y)(z) to (x, y, z)
    path = re.sub(r'\)\(', ', ', path)

    # Sanitize any SV keywords
    def kw_filter_repl(m: Match) -> str:
        return kwf(m.group(0))
    path = re.sub(r'\w+', kw_filter_repl, path)

    return path

def clog2(n: int) -> int:
    return (n-1).bit_length()

def is_pow2(x: int) -> bool:
    return (x > 0) and ((x & (x - 1)) == 0)

def roundup_pow2(x: int) -> int:
    return 1<<(x-1).bit_length()

def ref_is_internal(top_node: AddrmapNode, ref: Union[Node, PropertyReference]) -> bool:
    """
    Determine whether the reference is internal to the top node.

    For the sake of this exporter, root signals are treated as internal.
    """
    if isinstance(ref, Node):
        current_node = ref
    elif isinstance(ref, PropertyReference):
        current_node = ref.node

    while current_node is not None:
        if current_node == top_node:
            # reached top node without finding any external components
            # is internal!
            return True

        if current_node.external:
            # not internal!
            return False

        current_node = current_node.parent

    # A root signal was referenced, which dodged the top addrmap
    # This is considerd internal for this exporter
    return True


def do_slice(value: Union[VhdlInt, str], high: int, low: int, reduce=True) -> Union[VhdlInt, str]:
    if isinstance(value, str):
        # If string, assume this is an identifier. Append bit-slice
        if high == low and reduce:
            return f"{value}({low})"
        else:
            return f"{value}({high} downto {low})"
    else:
        # it is a VhdlInt literal. Slice it down
        mask = (1 << (high + 1)) - 1
        v = (value.value & mask) >> low

        if value.width is not None:
            w = high - low + 1
        else:
            w = None

        return VhdlInt(v, w, value.kind, value.allow_std_logic)

def do_bitswap(value: Union[VhdlInt, str]) -> Union[VhdlInt, str]:
    if isinstance(value, str):
        # If string, assume this is an identifier. Wrap in a function
        return f"bitswap({value})"
    else:
        # it is a VhdlInt literal. bitswap it
        assert value.width is not None # width must be known!
        v = value.value
        vswap = 0
        for _ in range(value.width):
            vswap = (vswap << 1) + (v & 1)
            v >>= 1
        return VhdlInt(vswap, value.width, value.kind, value.allow_std_logic)
