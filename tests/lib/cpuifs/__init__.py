from .passthrough import Passthrough
from .apb3 import APB3, FlatAPB3
from .apb4 import APB4, FlatAPB4
from .axi4lite import AXI4Lite, FlatAXI4Lite
from .avalon import Avalon, FlatAvalon
from .obi import OBI, FlatOBI

ALL_CPUIF = [
    Passthrough(),
    APB3(),
    FlatAPB3(),
    APB4(),
    FlatAPB4(),
    AXI4Lite(),
    FlatAXI4Lite(),
    Avalon(),
    FlatAvalon(),
    OBI(),
    FlatOBI(),
]
