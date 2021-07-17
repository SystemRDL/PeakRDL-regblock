import os
from typing import Union

import jinja2 as jj
from systemrdl.node import AddrmapNode, RootNode

from .addr_decode import AddressDecode
from .field_logic import FieldLogic
from .dereferencer import Dereferencer
from .readback_mux import ReadbackMux
from .signals import InferredSignal, SignalBase

from .cpuif.apb4 import APB4_Cpuif
from .hwif import Hwif
from .utils import get_always_ff_event

class RegblockExporter:
    def __init__(self, **kwargs):
        user_template_dir = kwargs.pop("user_template_dir", None)

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])


        self.top_node = None # type: AddrmapNode
        self.hwif = None # type: Hwif
        self.address_decode = AddressDecode(self)
        self.field_logic = FieldLogic(self)
        self.readback_mux = ReadbackMux(self)
        self.dereferencer = Dereferencer(self)
        self.default_resetsignal = InferredSignal("rst")


        if user_template_dir:
            loader = jj.ChoiceLoader([
                jj.FileSystemLoader(user_template_dir),
                jj.FileSystemLoader(os.path.dirname(__file__)),
                jj.PrefixLoader({
                    'user': jj.FileSystemLoader(user_template_dir),
                    'base': jj.FileSystemLoader(os.path.dirname(__file__)),
                }, delimiter=":")
            ])
        else:
            loader = jj.ChoiceLoader([
                jj.FileSystemLoader(os.path.dirname(__file__)),
                jj.PrefixLoader({
                    'base': jj.FileSystemLoader(os.path.dirname(__file__)),
                }, delimiter=":")
            ])

        self.jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined,
        )


    def export(self, node: Union[RootNode, AddrmapNode], output_path:str, **kwargs):
        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            self.top_node = node.top
        else:
            self.top_node = node


        cpuif_cls = kwargs.pop("cpuif_cls", APB4_Cpuif)
        hwif_cls = kwargs.pop("hwif_cls", Hwif)
        module_name = kwargs.pop("module_name", self.top_node.inst_name)
        package_name = kwargs.pop("package_name", module_name + "_pkg")

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])



        # TODO: Scan design...

        # TODO: derive this from somewhere
        cpuif_reset = self.default_resetsignal
        reset_signals = set([cpuif_reset, self.default_resetsignal])

        cpuif = cpuif_cls(
            self,
            cpuif_reset=cpuif_reset, # TODO:
            data_width=32, # TODO: derive from the accesswidth used by regs
            addr_width=32 # TODO:
        )

        self.hwif = hwif_cls(
            self,
            package_name=package_name,
        )

        # Build Jinja template context
        context = {
            "module_name": module_name,
            "data_width": 32, # TODO:
            "addr_width": 32, # TODO:
            "reset_signals": reset_signals,
            "cpuif_reset": cpuif_reset,
            "user_signals": [], # TODO:
            "interrupts": [], # TODO:
            "cpuif": cpuif,
            "hwif": self.hwif,
            "address_decode": self.address_decode,
            "field_logic": self.field_logic,
            "readback_mux": self.readback_mux,
            "get_always_ff_event": get_always_ff_event,
        }

        # Write out design
        template = self.jj_env.get_template("module_tmpl.sv")
        stream = template.stream(context)
        stream.dump(output_path)
