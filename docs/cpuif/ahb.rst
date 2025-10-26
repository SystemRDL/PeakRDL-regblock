AMBA AHB
========

Implements the register block using an
`AMBA AHB <https://developer.arm.com/documentation/ihi0033/latest/>`_
(Advanced High-performance Bus) CPU interface.

.. note::
    The AHB interface implementation provides a simplified subset of the full AHB protocol,
    optimized for register access. It supports single transfers with configurable data widths.

.. warning::
    Like other CPU interfaces in this exporter, the AHB ``HADDR`` input is interpreted
    as a byte-address. Address values should be byte-aligned according to the data width
    being used (e.g., for 32-bit transfers, addresses increment in steps of 4).

The AHB CPU interface comes in two i/o port flavors:

SystemVerilog Interface
    * Command line: ``--cpuif ahb``
    * Interface Definition: :download:`ahb_intf.sv <../../hdl-src/ahb_intf.sv>`
    * Class: :class:`peakrdl_regblock.cpuif.ahb.AHB_Cpuif`

Flattened inputs/outputs
    Flattens the interface into discrete input and output ports.

    * Command line: ``--cpuif ahb-flat``
    * Class: :class:`peakrdl_regblock.cpuif.ahb.AHB_Cpuif_flattened`


Supported Signals
-----------------

The AHB interface implementation includes the following signals:

Command signals (inputs):
    * ``HSEL`` - Slave select signal
    * ``HWRITE`` - Write enable (1 = write, 0 = read)
    * ``HTRANS[1:0]`` - Transfer type
    * ``HSIZE[2:0]`` - Transfer size
    * ``HADDR`` - Address bus
    * ``HWDATA`` - Write data bus

Response signals (outputs):
    * ``HRDATA`` - Read data bus
    * ``HREADY`` - Transfer complete indicator
    * ``HRESP`` - Transfer response (error status)

