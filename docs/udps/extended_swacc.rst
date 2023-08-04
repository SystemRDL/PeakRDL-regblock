.. _extended_swacc:

Read/Write-specific swacc
=========================

SystemRDL defines the ``swacc`` property, but it does not distinguish between
read and write operations - it is asserted on *all* software accesses.
Similarly, the spec defines ``swmod`` which gets asserted on software writes,
but can also get asserted if the field has on-read side-effects.

What if you just wanted a plain and simple strobe that is asserted when software
reads or writes a field? The ``rd_swacc`` and ``wr_swacc`` UDPs provide this
functionality.


Properties
----------
These UDP definitions, along with others supported by PeakRDL-regblock can be
enabled by compiling the following file along with your design:
:download:`regblock_udps.rdl <../../hdl-src/regblock_udps.rdl>`.

.. describe:: rd_swacc

    If true, infers an output signal ``hwif_out..rd_swacc`` that is asserted
    when accessed by a software read operation. The output signal is asserted
    on the same clock cycle that the field is being sampled during the software
    read operation.

    .. wavedrom::

        {"signal": [
            {"name": "clk",                "wave": "p...."},
            {"name": "hwif_in..next",      "wave": "x.=x.", "data": ["D"]},
            {"name": "hwif_out..rd_swacc", "wave": "0.10."}
        ]}


.. describe:: wr_swacc

    If true, infers an output signal ``hwif_out..wr_swacc`` that is asserted
    as the field is being modified by a software write operation.

    .. wavedrom::

        {"signal": [
            {"name": "clk",                "wave": "p....."},
            {"name": "hwif_out..value",    "wave": "=..=..", "data": ["old", "new"]},
            {"name": "hwif_out..wr_swacc", "wave": "0.10.."}
        ]}
