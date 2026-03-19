Wishbone Bus
============

Implements the register block using a
`Wishbone B4 <https://cdn.opencores.org/downloads/wbspec_b4.pdf>`_
CPU interface.

The wishbone interface comes in two i/o port flavors:

SystemVerilog Interface
    * Command line: ``--cpuif wishbone``
    * Interface Definition: :download:`wishbone_intf.sv <../../hdl-src/wishbone_intf.sv>`
    * Class: :class:`peakrdl_regblock.cpuif.wishbone.Wishbone_Cpuif`

Flattened inputs/outputs
    Flattens the interface into discrete input and output ports.

    * Command line: ``--cpuif wishbone-flat``
    * Class: :class:`peakrdl_regblock.cpuif.wishbone.Wishbone_Cpuif_flattened`


Implementation Details
----------------------
This implementation of the Wishbone protocol has the following features:
- Classic Wishbone Operations (SINGLE_READ and SINGLE_WRITE)
- Stall and Error optional output signals

Note that the ``cyc`` signal is not connected and it is a placeholder, since it
is redundant in wishbone classic operations.
Commands are captured based on ``stb``.
