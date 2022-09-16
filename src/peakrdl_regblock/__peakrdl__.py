from typing import TYPE_CHECKING

from .exporter import RegblockExporter
from .cpuif import apb3, apb4, axi4lite, passthrough

if TYPE_CHECKING:
    import argparse
    from systemrdl.node import AddrmapNode


# TODO: make this user-extensible
CPUIF_DICT = {
    "apb3": apb3.APB3_Cpuif,
    "apb3-flat": apb3.APB3_Cpuif_flattened,
    "apb4": apb4.APB4_Cpuif,
    "apb4-flat": apb4.APB4_Cpuif_flattened,
    "axi4-lite": axi4lite.AXI4Lite_Cpuif,
    "axi4-lite-flat": axi4lite.AXI4Lite_Cpuif_flattened,
    "passthrough": passthrough.PassthroughCpuif
}


class Exporter:
    short_desc = "Generate a SystemVerilog control/status register (CSR) block"

    def add_exporter_arguments(self, arg_group: 'argparse.ArgumentParser') -> None:
        arg_group.add_argument(
            "--cpuif",
            choices=CPUIF_DICT.keys(),
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
            "--pack-hwif-structs",
            dest="pack_hwif_structs",
            action="store_true",
            default=False,
            help="Enable use of packed structs for the HWIF types"
        )

    def do_export(self, top_node: 'AddrmapNode', options: 'argparse.Namespace') -> None:
        x = RegblockExporter()
        x.export(
            top_node,
            options.output,
            cpuif_cls=CPUIF_DICT[options.cpuif],
            module_name=options.module_name,
            package_name=options.package_name,
            reuse_hwif_typedefs=(options.type_style == "lexical"),
            retime_read_fanin=options.rt_read_fanin,
            retime_read_response=options.rt_read_response,
            pack_hwif_structs=options.pack_hwif_structs
        )
