from typing import TYPE_CHECKING, Any

from systemrdl.udp import UDPDefinition
from systemrdl.component import Addrmap

if TYPE_CHECKING:
    from systemrdl.node import Node

class CpuIf(UDPDefinition):
    name = "cpuif"
    valid_components = {Addrmap}
    valid_type = str

    def get_unassigned_default(self, node: 'Node') -> Any:
        return None


class AddrWidth(UDPDefinition):
    name = "addrwidth"
    valid_components = {Addrmap}
    valid_type = int

    def get_unassigned_default(self, node: 'Node') -> Any:
        return None
