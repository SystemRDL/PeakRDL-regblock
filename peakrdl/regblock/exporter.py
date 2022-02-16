import os
from typing import Union

import jinja2 as jj
from systemrdl.node import AddrmapNode, RootNode

from .addr_decode import AddressDecode
from .field_logic import FieldLogic
from .dereferencer import Dereferencer
from .readback import Readback

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
        self.min_read_latency = 0
        self.min_write_latency = 0

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
        reuse_hwif_typedefs = kwargs.pop("reuse_hwif_typedefs", True)

        # Pipelining options
        retime_read_fanin = kwargs.pop("retime_read_fanin", False)
        retime_read_response = kwargs.pop("retime_read_response", True)

        # Check for stray kwargs
        if kwargs:
            raise TypeError("got an unexpected keyword argument '%s'" % list(kwargs.keys())[0])

        self.min_read_latency = 0
        self.min_write_latency = 0
        if retime_read_fanin:
            self.min_read_latency += 1
        if retime_read_response:
            self.min_read_latency += 1

        # Scan the design for any unsupported features
        # Also collect pre-export information
        scanner = DesignScanner(self)
        scanner.do_scan()

        self.cpuif = cpuif_cls(
            self,
            cpuif_reset=self.top_node.cpuif_reset,
            data_width=scanner.cpuif_data_width,
            addr_width=self.top_node.size.bit_length()
        )

        self.hwif = Hwif(
            self,
            package_name=package_name,
            in_hier_signal_paths=scanner.in_hier_signal_paths,
            out_of_hier_signals=scanner.out_of_hier_signals,
            reuse_typedefs=reuse_hwif_typedefs,
        )

        self.readback = Readback(
            self,
            retime_read_fanin
        )

        # Build Jinja template context
        context = {
            "module_name": module_name,
            "user_out_of_hier_signals": scanner.out_of_hier_signals.values(),
            "cpuif": self.cpuif,
            "hwif": self.hwif,
            "get_resetsignal": self.dereferencer.get_resetsignal,
            "address_decode": self.address_decode,
            "field_logic": self.field_logic,
            "readback": self.readback,
            "get_always_ff_event": lambda resetsignal : get_always_ff_event(self.dereferencer, resetsignal),
            "retime_read_response": retime_read_response,
            "min_read_latency": self.min_read_latency,
            "min_write_latency": self.min_write_latency,
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
