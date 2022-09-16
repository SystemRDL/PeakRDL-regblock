AMBA APB
========

Both APB3 and APB4 standards are supported.

.. warning::
    Some IP vendors will incorrectly implement the address signalling
    assuming word-addresses. (that each increment of ``PADDR`` is the next word)

    For this exporter, values on the interface's ``PADDR`` input are interpreted
    as byte-addresses. (an APB interface with 32-bit wide data increments
    ``PADDR`` in steps of 4 for every word). Even though APB protocol does not
    allow for unaligned transfers, this is in accordance to the official AMBA
    specification.

    Be sure to double-check the interpretation of your interconnect IP. A simple
    bit-shift operation can be used to correct this if necessary.


APB3
----

Implements the register block using an
`AMBA 3 APB <https://developer.arm.com/documentation/ihi0024/b/Introduction/About-the-AMBA-3-APB>`_
CPU interface.

The APB3 CPU interface comes in two i/o port flavors:

SystemVerilog Interface
    Class: :class:`peakrdl_regblock.cpuif.apb3.APB3_Cpuif`

    Interface Definition: :download:`apb3_intf.sv <../../tests/lib/cpuifs/apb3/apb3_intf.sv>`

Flattened inputs/outputs
    Flattens the interface into discrete input and output ports.

    Class: :class:`peakrdl_regblock.cpuif.apb3.APB3_Cpuif_flattened`


APB4
----

Implements the register block using an
`AMBA 4 APB <https://developer.arm.com/documentation/ihi0024/d/?lang=en>`_
CPU interface.

The APB4 CPU interface comes in two i/o port flavors:

SystemVerilog Interface
    Class: :class:`peakrdl_regblock.cpuif.apb4.APB4_Cpuif`

    Interface Definition: :download:`apb4_intf.sv <../../tests/lib/cpuifs/apb4/apb4_intf.sv>`

Flattened inputs/outputs
    Flattens the interface into discrete input and output ports.

    Class: :class:`peakrdl_regblock.cpuif.apb4.APB4_Cpuif_flattened`
