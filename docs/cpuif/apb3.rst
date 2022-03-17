AMBA 3 APB
==========

Implements the register block using an
`AMBA 3 APB <https://developer.arm.com/documentation/ihi0024/b/Introduction/About-the-AMBA-3-APB>`_
CPU interface.

The APB3 CPU interface comes in two i/o port flavors:

SystemVerilog Interface
    Class: :class:`peakrdl.regblock.cpuif.apb3.APB3_Cpuif`

    Interface Definition: :download:`apb3_intf.sv <../../tests/lib/cpuifs/apb3/apb3_intf.sv>`

Flattened inputs/outputs
    Flattens the interface into discrete input and output ports.

    Class: :class:`peakrdl.regblock.cpuif.apb3.APB3_Cpuif_flattened`


.. warning::
    Some IP vendors will incorrectly implement the address signalling
    assuming word-addresses. (that each increment of ``PADDR`` is the next word)

    For this exporter, values on the interface's ``PADDR`` input are interpreted
    as byte-addresses. (a 32-bit APB bus increments ``PADDR`` in steps of 4)
    Although APB protocol does not allow for unaligned transfers, this is in
    accordance to the official AMBA bus specification.

    Be sure to double-check the interpretation of your interconnect IP. A simple
    bit-shift operation can be used to correct this if necessary.
