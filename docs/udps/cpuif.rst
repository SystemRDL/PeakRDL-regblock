.. _cpuif:

CPU Interface
=============

Properties
----------
The CPU interface for the registers can be specified with the following properties:

.. literalinclude:: ../../hdl-src/regblock_udps.rdl
    :lines: 40-48

This UDP definition, along with others supported by PeakRDL-regblock can be
enabled by compiling the following file along with your design:
:download:`regblock_udps.rdl <../../hdl-src/regblock_udps.rdl>`.

.. describe:: cpuif

    *   Assigned value is a string.
    *   Specifies the CPU interface type to access the registers.

.. describe:: addrwidth

    *   Assigned value is a longint unsigned.
    *   Specifies the width of the CPU interface's address bus.

Example
-------

In this example, an axi4-lite CPU interface is specified with an address bus
width of 8.

.. code-block:: systemrdl
    :emphasize-lines: 4

    addrmap top {
        cpuif = "axi4-lite";
        addrwidth = 8;

        reg {
            field {} rst;
            field {} en;
            field {} start;
            field {} stop;
        } control;

        reg {
            field {} running;
            field {} done;
        } status;
    };
