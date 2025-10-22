from typing import Type, Optional, List
import functools

from .base import Simulator
from .questa import Questa
from .xilinx import XilinxXSIM
from .xcelium import Xcelium
from .stub import StubSimulator

ALL_SIMULATORS: List[Simulator]
ALL_SIMULATORS = [
    Questa,
    XilinxXSIM,
    Xcelium,
    StubSimulator,
]

@functools.lru_cache()
def get_simulator_cls(name: str) -> Optional[Type[Simulator]]:
    if name == "skip":
        return None

    if name == "auto":
        # Find the first simulator that is installed
        for sim_cls in ALL_SIMULATORS:
            if sim_cls is StubSimulator:
                # Never offer the stub as an automatic option
                continue
            if sim_cls.is_installed():
                return sim_cls
        raise ValueError("Could not find any installed simulators")

    # Look up which explicit simulator name was specified
    for sim_cls in ALL_SIMULATORS:
        if sim_cls.name == name:
            if not sim_cls.is_installed():
                raise ValueError("Simulator '%s' is not installed" % sim_cls.name)
            return sim_cls
    raise RuntimeError
