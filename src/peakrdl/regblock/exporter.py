import os
from typing import Union, Any, Type

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
    def __init__(self, **kwargs: Any) -> None:
        # Check for stray kwargs
        if kwargs:
            raise TypeError(f"got an unexpected keyword argument '{list(kwargs.keys())[0]}'")


        self.top_node = None # type: AddrmapNode
        self.hwif = None # type: Hwif
        self.cpuif = None # type: CpuifBase
        self.address_decode = AddressDecode(self)
        self.field_logic = FieldLogic(self)
        self.readback = None # type: Readback
        self.dereferencer = Dereferencer(self)
        self.min_read_latency = 0
        self.min_write_latency = 0

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


    def export(self, node: Union[RootNode, AddrmapNode], output_dir:str, **kwargs: Any) -> None:
        """
        Parameters
        ----------
        node: AddrmapNode
            Top-level SystemRDL node to export.
        output_dir: str
            Path to the output directory where generated SystemVerilog will be written.
            Output includes two files: a module definition and package definition.
        cpuif_cls: :class:`peakrdl.regblock.cpuif.CpuifBase`
            Specify the class type that implements the CPU interface of your choice.
            Defaults to AMBA APB3.
        module_name: str
            Override the SystemVerilog module name. By default, the module name
            is the top-level node's name.
        package_name: str
            Override the SystemVerilog package name. By default, the package name
            is the top-level node's name with a "_pkg" suffix.
        reuse_hwif_typedefs: bool
            By default, the exporter will attempt to re-use hwif struct definitions for
            nodes that are equivalent. This allows for better modularity and type reuse.
            Struct type names are derived using the SystemRDL component's type
            name and declared lexical scope path.

            If this is not desireable, override this parameter to ``False`` and structs
            will be generated more naively using their hierarchical paths.
        retime_read_fanin: bool
            Set this to ``True`` to enable additional read path retiming.
            For large register blocks that operate at demanding clock rates, this
            may be necessary in order to manage large readback fan-in.

            The retiming flop stage is automatically placed in the most optimal point in the
            readback path so that logic-levels and fanin are minimized.

            Enabling this option will increase read transfer latency by 1 clock cycle.
        retime_read_response: bool
            Set this to ``True`` to enable an additional retiming flop stage between
            the readback mux and the CPU interface response logic.
            This option may be beneficial for some CPU interfaces that implement the
            response logic fully combinationally. Enabling this stage can better
            isolate timing paths in the register file from the rest of your system.

            Enabling this when using CPU interfaces that already implement the
            response path sequentially may not result in any meaningful timing improvement.

            Enabling this option will increase read transfer latency by 1 clock cycle.
        """
        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            self.top_node = node.top
        else:
            self.top_node = node


        cpuif_cls = kwargs.pop("cpuif_cls", APB3_Cpuif) # type: Type[CpuifBase]
        module_name = kwargs.pop("module_name", self.top_node.inst_name) # type: str
        package_name = kwargs.pop("package_name", module_name + "_pkg") # type: str
        reuse_hwif_typedefs = kwargs.pop("reuse_hwif_typedefs", True) # type: bool

        # Pipelining options
        retime_read_fanin = kwargs.pop("retime_read_fanin", False) # type: bool
        retime_read_response = kwargs.pop("retime_read_response", True) # type: bool

        # Check for stray kwargs
        if kwargs:
            raise TypeError(f"got an unexpected keyword argument '{list(kwargs.keys())[0]}'")

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
