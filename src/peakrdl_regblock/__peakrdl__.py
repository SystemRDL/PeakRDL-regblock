from typing import TYPE_CHECKING, Dict, Type
import functools

from peakrdl.plugins.exporter import ExporterSubcommandPlugin #pylint: disable=import-error
from peakrdl.config import schema #pylint: disable=import-error

from .exporter import RegblockExporter
from .cpuif import apb3, apb4, axi4lite, passthrough, CpuifBase
from .udps import ALL_UDPS
from . import entry_points

if TYPE_CHECKING:
    import argparse
    from systemrdl.node import AddrmapNode


class Exporter(ExporterSubcommandPlugin):
    short_desc = "Generate a SystemVerilog control/status register (CSR) block"

    udp_definitions = ALL_UDPS

    cfg_schema = {
        "cpuifs": {"*": schema.PythonObjectImport()}
    }

    @functools.lru_cache()
    def get_cpuifs(self) -> Dict[str, Type[CpuifBase]]:

        # All built-in CPUIFs
        cpuifs = {
            "apb3": apb3.APB3_Cpuif,
            "apb3-flat": apb3.APB3_Cpuif_flattened,
            "apb4": apb4.APB4_Cpuif,
            "apb4-flat": apb4.APB4_Cpuif_flattened,
            "axi4-lite": axi4lite.AXI4Lite_Cpuif,
            "axi4-lite-flat": axi4lite.AXI4Lite_Cpuif_flattened,
            "passthrough": passthrough.PassthroughCpuif
        }

        # Load any cpuifs specified via entry points
        for ep, dist in entry_points.get_entry_points("peakrdl_regblock.cpuif"):
            name = ep.name
            cpuif = ep.load()
            if name in cpuifs:
                raise RuntimeError(f"A plugin for 'peakrdl-regblock' tried to load cpuif '{name}' but it already exists")
            if not issubclass(cpuif, CpuifBase):
                raise RuntimeError(f"A plugin for 'peakrdl-regblock' tried to load cpuif '{name}' but it not a CpuifBase class")
            cpuifs[name] = cpuif

        # Load any CPUIFs via config import
        for name, cpuif in self.cfg['cpuifs'].items():
            if name in cpuifs:
                raise RuntimeError(f"A plugin for 'peakrdl-regblock' tried to load cpuif '{name}' but it already exists")
            if not issubclass(cpuif, CpuifBase):
                raise RuntimeError(f"A plugin for 'peakrdl-regblock' tried to load cpuif '{name}' but it not a CpuifBase class")
            cpuifs[name] = cpuif

        return cpuifs


    def add_exporter_arguments(self, arg_group: 'argparse.ArgumentParser') -> None:
        cpuifs = self.get_cpuifs()

        arg_group.add_argument(
            "--cpuif",
            choices=cpuifs.keys(),
            default="apb3",
            help="Select the CPU interface protocol to use [apb3]"
        )

        arg_group.add_argument(
            "--module-name",
            metavar="NAME",
            default=None,
            help="Override the SystemVerilog module name"
        )

        arg_group.add_argument(
            "--package-name",
            metavar="NAME",
            default=None,
            help="Override the SystemVerilog package name"
        )

        arg_group.add_argument(
            "--rt-read-fanin",
            action="store_true",
            default=False,
            help="Enable additional read path retiming. Good for register blocks with large readback fan-in"
        )
        arg_group.add_argument(
            "--rt-read-response",
            action="store_true",
            default=False,
            help="Enable additional retiming stage between readback fan-in and cpu interface"
        )
        arg_group.add_argument(
            "--type-style",
            dest="type_style",
            choices=['lexical', 'hier'],
            default="lexical",
            help="""Choose how HWIF struct type names are generated.
            The 'lexical' style will use RDL lexical scope & type names where
            possible and attempt to re-use equivalent type definitions.
            The 'hier' style uses component's hierarchy as the struct type name. [lexical]
            """
        )
        arg_group.add_argument(
            "--hwif-report",
            action="store_true",
            default=False,
            help="Generate a HWIF report file"
        )

        arg_group.add_argument(
            "--addr-width",
            type=int,
            default=None,
            help="""Override the CPU interface's address width. By default,
            address width is sized to the contents of the regblock.
            """
        )


    def do_export(self, top_node: 'AddrmapNode', options: 'argparse.Namespace') -> None:
        cpuifs = self.get_cpuifs()

        x = RegblockExporter()
        x.export(
            top_node,
            options.output,
            cpuif_cls=cpuifs[options.cpuif],
            module_name=options.module_name,
            package_name=options.package_name,
            reuse_hwif_typedefs=(options.type_style == "lexical"),
            retime_read_fanin=options.rt_read_fanin,
            retime_read_response=options.rt_read_response,
            generate_hwif_report=options.hwif_report,
            address_width=options.addr_width,
        )
