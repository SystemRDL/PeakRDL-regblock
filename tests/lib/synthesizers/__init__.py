from typing import List, Optional, Type
import functools

from .base import Synthesizer
from .vivado import Vivado

ALL_SYNTHESIZERS: List[Synthesizer]
ALL_SYNTHESIZERS = [
    Vivado,
]

@functools.lru_cache()
def get_synthesizer_cls(name: str) -> Optional[Type[Synthesizer]]:
    if name == "skip":
        return None

    if name == "auto":
        # Find the first tool that is installed
        for synth_cls in ALL_SYNTHESIZERS:
            if synth_cls.is_installed():
                return synth_cls
        raise ValueError("Could not find any installed synthesis tools")

    # Look up which explicit synth tool name was specified
    for synth_cls in ALL_SYNTHESIZERS:
        if synth_cls.name == name:
            if not synth_cls.is_installed():
                raise ValueError("Synthesis tool '%s' is not installed" % synth_cls.name)
            return synth_cls
    raise RuntimeError
