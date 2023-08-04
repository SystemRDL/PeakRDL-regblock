External Components
===================
SystemRDL allows some component instances to be defined as "external" elements
of an address space definition. In the context of this regblock generator,
the implementation of an external component is left up to the designer. When
generating the RTL for a regblock, the implementations of external components
are omitted and instead a user-interface is presented on the
``hwif_in``/``hwif_out`` i/o structs.

External component signals on the hardware interface closely follow the semantics
of the :ref:`cpuif_protocol`.


Things you should know
----------------------

* By default external ``hwif_out`` signals are driven combinationally. An
  optional output retiming stage can be enabled if needed.
* Due to the uncertain access latency of external components, the regblock will
  always enforce that only one outstanding transaction to an external component
  at a time. This is enforced even if the CPUIF is capable of pipelined accesses
  such as AXI4-Lite.


External Registers
------------------
External registers can be useful if it is necessary to implement a register that
cannot easily be expressed using SystemRDL semantics. This could be a unique
access policy, or FIFO-like push/pop registers.

External registers are annotated as such by using the ``external`` keyword:

.. code-block:: systemrdl

    // An internal register
    my_reg int_reg;

    // An external register
    external my_reg ext_reg;

Request
^^^^^^^
hwif_out..req
    When asserted, a read or write transfer will be initiated.
    Qualifies all other request signals.

    If the register is wide (``regwidth`` > ``accesswidth``), then the
    ``hwif_out..req`` will consist of multiple bits, representing the access
    strobe for each sub-word of the register.

    If the register does not contain any readable fields, this strobe will be
    suppressed for read operations.

    If the register does not contain any writable readable fields, this strobe
    will be suppressed for write operations.

hwif_out..req_is_wr
    If ``1``, denotes that the current transfer is a write. Otherwise transfer is
    a read.

hwif_out..wr_data
    Data to be written for the write transfer. This signal is ignored for read
    transfers.

    The bit-width of this signal always matches the CPUIF's bus width,
    regardless of the regwidth.

    If the register does not contain any writable fields, this signal is omitted.

hwif_out..wr_biten
    Active-high bit-level write-enable strobes.
    Only asserted bit positions will change the register value during a write
    transfer.

    If the register does not contain any writable fields, this signal is omitted.


Read Response
^^^^^^^^^^^^^
hwif_in..rd_ack
    Single-cycle strobe indicating a read transfer has completed.
    Qualifies all other read response signals.

    If the transfer is always completed in the same cycle, it is acceptable to
    tie this signal to ``hwif_out..req && !hwif_out..req_is_wr``.

    If the register does not contain any readable fields, this signal is omitted.

hwif_in..rd_data
    Read response data.

    If the register does not contain any readable fields, this signal is omitted.

Write Response
^^^^^^^^^^^^^^
hwif_in..wr_ack
    Single-cycle strobe indicating a write transfer has completed.

    If the transfer is always completed in the same cycle, it is acceptable to
    tie this signal to ``hwif_out..req && hwif_out..req_is_wr``.

    If the register does not contain any writable fields, this signal is omitted.



External Blocks
---------------
Broader external address regions can be represented by external block-like
components such as ``addrmap``, ``regfile`` or ``mem`` elements.

To ensure address decoding for external blocks is simple (only requires simple bit-pruning),
blocks that are external to an exported regblock shall be aligned to their size.

Request
^^^^^^^
hwif_out..req
    When asserted, a read or write transfer will be initiated.
    Qualifies all other request signals.

hwif_out..addr
    Byte-address of the transfer.

    Address is always relative to the block's local addressing. i.e: The first
    byte within an external block is represented as ``hwif_out..addr`` == 0,
    regardless of the absolute address of the block.

hwif_out..req_is_wr
    If ``1``, denotes that the current transfer is a write. Otherwise transfer is
    a read.

hwif_out..wr_data
    Data to be written for the write transfer. This signal is ignored for read
    transfers.

    The bit-width of this signal always matches the CPUIF's bus width,
    regardless of the contents of the block.

hwif_out..wr_biten
    Active-high bit-level write-enable strobes.
    Only asserted bit positions will change the register value during a write
    transfer.

Read Response
^^^^^^^^^^^^^
hwif_in..rd_ack
    Single-cycle strobe indicating a read transfer has completed.
    Qualifies all other read response signals.

hwif_in..rd_data
    Read response data.

Write Response
^^^^^^^^^^^^^^
hwif_in..wr_ack
    Single-cycle strobe indicating a write transfer has completed.
