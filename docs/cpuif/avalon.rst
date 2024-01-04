Intel Avalon
============

Implements the register block using an
`Intel Avalon MM <https://www.intel.com/content/www/us/en/docs/programmable/683091/22-3/memory-mapped-interfaces.html>`_
CPU interface.

The Avalon interface comes in two i/o port flavors:

SystemVerilog Interface
    * Command line: ``--cpuif avalon-mm``
    * Interface Definition: :download:`avalon_mm_intf.sv <../../hdl-src/avalon_mm_intf.sv>`
    * Class: :class:`peakrdl_regblock.cpuif.avalon.Avalon_Cpuif`

Flattened inputs/outputs
    Flattens the interface into discrete input and output ports.

    * Command line: ``--cpuif avalon-mm-flat``
    * Class: :class:`peakrdl_regblock.cpuif.avalon.Avalon_Cpuif_flattened`


Implementation Details
----------------------
This implementation of the Avalon protocol has the following features:

* Interface uses word addressing.
* Supports `pipelined transfers <https://www.intel.com/content/www/us/en/docs/programmable/683091/22-3/pipelined-transfers.html>`_
* Responses may have variable latency

  In most cases, latency is fixed and is determined by how many retiming
  stages are enabled in your design.
  However if your design contains external components, access latency is
  not guaranteed to be uniform.
