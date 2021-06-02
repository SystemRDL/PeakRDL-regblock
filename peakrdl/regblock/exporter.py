import os
from typing import TYPE_CHECKING

import jinja2 as jj
from systemrdl.node import Node, RootNode

from .addr_decode import AddressDecode
from .field_logic import FieldLogic
from .dereferencer import Dereferencer
from .readback_mux import ReadbackMux
from .signals import InferredSignal

from .cpuif.apb4 import APB4_Cpuif
from .hwif.struct import StructHwif

class RegblockExporter:
    def __init__(self, **kwargs):
        user_template_dir = kwargs.pop("user_template_dir", None)

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])

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


    def export(self, node:Node, output_path:str, **kwargs):
        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            node = node.top

        cpuif_cls = kwargs.pop("cpuif_cls", APB4_Cpuif)
        hwif_cls = kwargs.pop("hwif_cls", StructHwif)
        module_name = kwargs.pop("module_name", node.inst_name)
        package_name = kwargs.pop("package_name", module_name + "_pkg")

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])



        # TODO: Scan design...

        # TODO: derive this from somewhere
        cpuif_reset = InferredSignal("rst")
        reset_signals = [cpuif_reset]

        cpuif = cpuif_cls(
            self,
            cpuif_reset=cpuif_reset, # TODO:
            data_width=32, # TODO:
            addr_width=32 # TODO:
        )

        hwif = hwif_cls(
            self,
            top_node=node,
            package_name=package_name,
        )

        address_decode = AddressDecode(self, node)
        field_logic = FieldLogic(self, node)
        readback_mux = ReadbackMux(self, node)
        dereferencer = Dereferencer(self, hwif, field_logic, node)

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
            "hwif": hwif,
            "address_decode": address_decode,
            "field_logic": field_logic,
            "readback_mux": readback_mux,
        }

        # Write out design
        template = self.jj_env.get_template("module_tmpl.sv")
        stream = template.stream(context)
        stream.dump(output_path)
