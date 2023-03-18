Introduction
============

Although the official SystemRDL spec defines numerous properties that allow you
to define complex register map structures, sometimes they are not enough to
accurately describe a necessary feature. Fortunately the SystemRDL spec allows
the language to be extended using "User Defined Properties" (UDPs). The
PeakRDL-regblock tool understands several UDPs that are described in this
section.

To enable these UDPs, compile this RDL file prior to the rest of your design:
:download:`regblock_udps.rdl <../../hdl-src/regblock_udps.rdl>`.

.. list-table:: Summary of UDPs
    :header-rows: 1

    *   - Name
        - Component
        - Type
        - Description

    *   - buffer_reads
        - reg
        - boolean
        - If set, reads from the register are double-buffered.

          See: :ref:`read_buffering`.

    *   - rbuffer_trigger
        - reg
        - reference
        - Defines the buffered read load trigger.

          See: :ref:`read_buffering`.

    *   - buffer_writes
        - reg
        - boolean
        - If set, writes to the register are double-buffered.

          See: :ref:`write_buffering`.

    *   - wbuffer_trigger
        - reg
        - reference
        - Defines the buffered write commit trigger.

          See: :ref:`write_buffering`.

    *   - rd_swacc
        - field
        - boolean
        - Enables an output strobe that is asserted on sw reads.

          See: :ref:`extended_swacc`.

    *   - wr_swacc
        - field
        - boolean
        - Enables an output strobe that is asserted on sw writes.

          See: :ref:`extended_swacc`.
