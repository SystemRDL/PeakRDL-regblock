import os
from typing import Union

import jinja2 as jj
from systemrdl.node import AddrmapNode, RootNode
from systemrdl.walker import RDLWalker

from .addr_decode import AddressDecode
from .field_logic import FieldLogic
from .dereferencer import Dereferencer
from .readback import Readback
from .signals import InferredSignal, RDLSignal

from .cpuif import CpuifBase
from .cpuif.apb3 import APB3_Cpuif
from .hwif import Hwif
from .utils import get_always_ff_event
from .scan_design import DesignScanner

class RegblockExporter:
    def __init__(self, **kwargs):
        user_template_dir = kwargs.pop("user_template_dir", None)

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])


        self.top_node = None # type: AddrmapNode
        self.hwif = None # type: Hwif
        self.cpuif = None # type: CpuifBase
        self.address_decode = AddressDecode(self)
        self.field_logic = FieldLogic(self)
        self.readback = None # type: Readback
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


    def export(self, node: Union[RootNode, AddrmapNode], output_dir:str, **kwargs):
        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            self.top_node = node.top
        else:
            self.top_node = node


        cpuif_cls = kwargs.pop("cpuif_cls", APB3_Cpuif)
        module_name = kwargs.pop("module_name", self.top_node.inst_name)
        package_name = kwargs.pop("package_name", module_name + "_pkg")

        # Pipelining options
        retime_read_fanin = kwargs.pop("retime_read_fanin", False)
        retime_read_response = kwargs.pop("retime_read_response", True)

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])


        # Scan the design for any unsupported features
        # Also collect pre-export information
        scanner = DesignScanner(self)
        RDLWalker().walk(self.top_node, scanner)
        if scanner.msg.had_error:
            scanner.msg.fatal(
                "Unable to export due to previous errors"
            )
            raise ValueError

        cpuif_reset_tmp = self.top_node.cpuif_reset
        if cpuif_reset_tmp:
            cpuif_reset = RDLSignal(cpuif_reset_tmp)
        else:
            cpuif_reset = self.default_resetsignal
        reset_signals = set([cpuif_reset, self.default_resetsignal])

        self.cpuif = cpuif_cls(
            self,
            cpuif_reset=cpuif_reset,
            data_width=scanner.cpuif_data_width,
            addr_width=self.top_node.size.bit_length()
        )

        self.hwif = Hwif(
            self,
            package_name=package_name,
        )

        self.readback = Readback(
            self,
            retime_read_fanin
        )

        # Build Jinja template context
        context = {
            "module_name": module_name,
            "reset_signals": reset_signals,
            "user_signals": [], # TODO:
            "interrupts": [], # TODO:
            "cpuif": self.cpuif,
            "hwif": self.hwif,
            "address_decode": self.address_decode,
            "field_logic": self.field_logic,
            "readback": self.readback,
            "get_always_ff_event": get_always_ff_event,
            "retime_read_response": retime_read_response,
        }

        # Write out design
        package_file_path = os.path.join(output_dir, package_name + ".sv")
        template = self.jj_env.get_template("package_tmpl.sv")
        stream = template.stream(context)
        stream.dump(package_file_path)

        module_file_path = os.path.join(output_dir, module_name + ".sv")
        template = self.jj_env.get_template("module_tmpl.sv")
        stream = template.stream(context)
        stream.dump(module_file_path)
