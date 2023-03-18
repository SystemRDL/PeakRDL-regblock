from typing import TYPE_CHECKING, Optional

from systemrdl.walker import RDLListener, RDLWalker, WalkerAction

if TYPE_CHECKING:
    from systemrdl.node import Node, RegNode, FieldNode, SignalNode, AddressableNode
    from .exporter import RegblockExporter

class DesignValidator(RDLListener):
    """
    Performs additional rule-checks on the design that check for limitations
    imposed by this exporter.
    """
    def __init__(self, exp:'RegblockExporter') -> None:
        self.exp = exp
        self.msg = exp.top_node.env.msg

    def do_validate(self) -> None:
        RDLWalker().walk(self.exp.top_node, self)
        if self.msg.had_error:
            self.msg.fatal(
                "Unable to export due to previous errors"
            )

    def enter_Component(self, node: 'Node') -> Optional[WalkerAction]:
        if node.external and (node != self.exp.top_node):
            self.msg.error(
                "Exporter does not support external components",
                node.inst.inst_src_ref
            )
            # Do not inspect external components. None of my business
            return WalkerAction.SkipDescendants
        return None

    def enter_Signal(self, node: 'SignalNode') -> None:
        # If encountering a CPUIF reset that is nested within the register model,
        # warn that it will be ignored.
        # Only cpuif resets in the top-level node or above will be honored
        if node.get_property('cpuif_reset') and (node.parent != self.exp.top_node):
            self.msg.warning(
                "Only cpuif_reset signals that are instantiated in the top-level "
                "addrmap or above will be honored. Any cpuif_reset signals nested "
                "within children of the addrmap being exported will be ignored.",
                node.inst.inst_src_ref
            )

    def enter_AddressableComponent(self, node: 'AddressableNode') -> None:
        # All registers must be aligned to the internal data bus width
        alignment = self.exp.cpuif.data_width_bytes
        if (node.raw_address_offset % alignment) != 0:
            self.msg.error(
                "Unaligned registers are not supported. Address offset of "
                f"instance '{node.inst_name}' must be a multiple of {alignment}",
                node.inst.inst_src_ref
            )
        if node.is_array and (node.array_stride % alignment) != 0:
            self.msg.error(
                "Unaligned registers are not supported. Address stride of "
                f"instance array '{node.inst_name}' must be a multiple of {alignment}",
                node.inst.inst_src_ref
            )

    def enter_Reg(self, node: 'RegNode') -> None:
        # accesswidth of wide registers must be consistent within the register block
        accesswidth = node.get_property('accesswidth')
        regwidth = node.get_property('regwidth')

        if accesswidth < regwidth:
            # register is 'wide'
            if accesswidth != self.exp.cpuif.data_width:
                self.msg.error(
                    f"Multi-word registers that have an accesswidth ({accesswidth}) "
                    "that is inconsistent with this regblock's CPU bus width "
                    f"({self.exp.cpuif.data_width}) are not supported.",
                    node.inst.inst_src_ref
                )


    def enter_Field(self, node: 'FieldNode') -> None:
        parent_accesswidth = node.parent.get_property('accesswidth')
        parent_regwidth = node.parent.get_property('regwidth')
        if (
            (parent_accesswidth < parent_regwidth)
            and (node.lsb // parent_accesswidth) != (node.msb // parent_accesswidth)
        ):
            # field spans multiple sub-words
            if node.is_sw_writable and not node.parent.get_property('buffer_writes'):
                # ... and is writable without the protection of double-buffering
                # Enforce 10.6.1-f
                self.msg.error(
                    f"Software-writable field '{node.inst_name}' shall not span"
                    " multiple software-accessible subwords. Consider enabling"
                    " write double-buffering.\n"
                    "For more details, see: https://peakrdl-regblock.readthedocs.io/en/latest/udps/write_buffering.html",
                    node.inst.inst_src_ref
                )

            if node.get_property('onread') is not None and not node.parent.get_property('buffer_reads'):
                # ... is modified by an onread action without the atomicity of read buffering
                # Enforce 10.6.1-f
                self.msg.error(
                    f"The field '{node.inst_name}' spans multiple software-accessible"
                    " subwords and is modified on-read, making it impossible to"
                    " access its value correctly. Consider enabling read"
                    " double-buffering. \n"
                    "For more details, see: https://peakrdl-regblock.readthedocs.io/en/latest/udps/read_buffering.html",
                    node.inst.inst_src_ref
                )
