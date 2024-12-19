Introduction
============

The CPU interface logic layer provides an abstraction between the
application-specific bus protocol and the internal register file logic.
When exporting a design, you can select from a variety of popular CPU interface
protocols. These are described in more detail in the pages that follow.


Bus Width
^^^^^^^^^
The CPU interface bus width is automatically determined from the contents of the
design being exported. The bus width is equal to the widest ``accesswidth``
encountered in the design.


Addressing
^^^^^^^^^^

The regblock exporter will always generate its address decoding logic using local
address offsets. The absolute address offset of your device shall be
handled by your system interconnect, and present addresses to the regblock that
only include the local offset.

For example, consider a fictional AXI4-Lite device that:

- Consumes 4 kB of address space (``0x000``-``0xFFF``).
- The device is instantiated in your system at global address range ``0x30_0000 - 0x50_0FFF``.
- After decoding transactions destined to the device, the system interconnect shall
  ensure that AxADDR values are presented to the device as relative addresses - within
  the range of ``0x000``-``0xFFF``.
- If care is taken to align the global address offset to the size of the device,
  creating a relative address is as simple as pruning down address bits.

By default, the bit-width of the address bus will be the minimum size to span the contents
of the register block. If needed, the address width can be overridden to a larger range.
