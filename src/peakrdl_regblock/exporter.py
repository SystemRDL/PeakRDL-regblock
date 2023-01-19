import os
from typing import Union, Any, Type, Optional

import jinja2 as jj
from systemrdl.node import AddrmapNode, RootNode

from .addr_decode import AddressDecode
from .field_logic import FieldLogic
from .dereferencer import Dereferencer
from .readback import Readback
from .identifier_filter import kw_filter as kwf

from .utils import get_always_ff_event
from .scan_design import DesignScanner
from .validate_design import DesignValidator
from .cpuif import CpuifBase
from .cpuif.apb4 import APB4_Cpuif
from .hwif import Hwif
from .write_buffering import WriteBuffering
from .read_buffering import ReadBuffering

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
        self.write_buffering = WriteBuffering(self)
        self.read_buffering = ReadBuffering(self)
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
        cpuif_cls: :class:`peakrdl_regblock.cpuif.CpuifBase`
            Specify the class type that implements the CPU interface of your choice.
            Defaults to AMBA APB4.
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
        generate_hwif_report: bool
            If set, generates a hwif report that can help designers understand
            the contents of the ``hwif_in`` and ``hwif_out`` structures.
        address_width: int
            Override the CPU interface's address width. By default, address width
            is sized to the contents of the regblock.
        """
        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            self.top_node = node.top
        else:
            self.top_node = node
        msg = self.top_node.env.msg


        cpuif_cls = kwargs.pop("cpuif_cls", None) or APB4_Cpuif # type: Type[CpuifBase]
        module_name = kwargs.pop("module_name", None) or kwf(self.top_node.inst_name) # type: str
        package_name = kwargs.pop("package_name", None) or (module_name + "_pkg") # type: str
        reuse_hwif_typedefs = kwargs.pop("reuse_hwif_typedefs", True) # type: bool
        generate_hwif_report = kwargs.pop("generate_hwif_report", False) # type: bool
        user_addr_width = kwargs.pop("address_width", None) # type: Optional[int]

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

        addr_width = self.top_node.size.bit_length()
        if user_addr_width is not None:
            if user_addr_width < addr_width:
                msg.fatal(f"User-specified address width shall be greater than or equal to {addr_width}.")
            addr_width = user_addr_width

        # Scan the design for pre-export information
        scanner = DesignScanner(self)
        scanner.do_scan()

        if generate_hwif_report:
            path = os.path.join(output_dir, f"{module_name}_hwif.rpt")
            hwif_report_file = open(path, "w", encoding='utf-8') # pylint: disable=consider-using-with
        else:
            hwif_report_file = None

        # Construct exporter components
        self.cpuif = cpuif_cls(
            self,
            cpuif_reset=self.top_node.cpuif_reset,
            data_width=scanner.cpuif_data_width,
            addr_width=addr_width
        )
        self.hwif = Hwif(
            self,
            package_name=package_name,
            in_hier_signal_paths=scanner.in_hier_signal_paths,
            out_of_hier_signals=scanner.out_of_hier_signals,
            reuse_typedefs=reuse_hwif_typedefs,
            hwif_report_file=hwif_report_file,
        )
        self.readback = Readback(
            self,
            retime_read_fanin
        )

        # Validate that there are no unsupported constructs
        validator = DesignValidator(self)
        validator.do_validate()

        # Build Jinja template context
        context = {
            "module_name": module_name,
            "user_out_of_hier_signals": scanner.out_of_hier_signals.values(),
            "has_writable_msb0_fields": scanner.has_writable_msb0_fields,
            "has_buffered_write_regs": scanner.has_buffered_write_regs,
            "has_buffered_read_regs": scanner.has_buffered_read_regs,
            "cpuif": self.cpuif,
            "hwif": self.hwif,
            "write_buffering": self.write_buffering,
            "read_buffering": self.read_buffering,
            "get_resetsignal": self.dereferencer.get_resetsignal,
            "address_decode": self.address_decode,
            "field_logic": self.field_logic,
            "readback": self.readback,
            "get_always_ff_event": lambda resetsignal : get_always_ff_event(self.dereferencer, resetsignal),
            "retime_read_response": retime_read_response,
            "min_read_latency": self.min_read_latency,
            "min_write_latency": self.min_write_latency,
            "kwf": kwf,
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

        if hwif_report_file:
            hwif_report_file.close()
