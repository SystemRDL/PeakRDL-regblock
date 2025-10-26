Open Bus Interface (OBI)
========================

Implements the register block using an `OBI <https://github.com/openhwgroup/obi>`_
CPU interface.

The OBI interface comes in two i/o port flavors:

SystemVerilog Interface
    * Command line: ``--cpuif obi``
    * Interface Definition: :download:`obi_intf.sv <../../hdl-src/obi_intf.sv>`
    * Class: :class:`peakrdl_regblock.cpuif.obi.OBI_Cpuif`

Flattened inputs/outputs
    Flattens the interface into discrete input and output ports.

    * Command line: ``--cpuif obi-flat``
    * Class: :class:`peakrdl_regblock.cpuif.obi.OBI_Cpuif_flattened`
