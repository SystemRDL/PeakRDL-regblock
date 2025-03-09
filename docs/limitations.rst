Known Limitations
=================

Not all SystemRDL features are supported by this exporter. For a listing of
supported properties, see the appropriate property listing page in the sections
that follow.


Alias Registers
---------------
Registers instantiated using the ``alias`` keyword are not supported yet.


Unaligned Registers
-------------------
All address offsets & strides shall be a multiple of the cpuif bus width used. Specifically:

* Bus width is inferred by the maximum accesswidth used in the regblock.
* Each component's address and array stride shall be aligned to the bus width.


Uniform accesswidth
-------------------
All registers within a register block shall use the same accesswidth.

One exception is that registers with regwidth that is narrower than the cpuif
bus width are permitted, provided that their regwidth is equal to their accesswidth.

For example:

.. code-block:: systemrdl

    // (Largest accesswidth used is 32, therefore the CPUIF bus width is 32)

    reg {
        regwidth = 32;
        accesswidth = 32;
    } reg_a @ 0x00; // OK. Regular 32-bit register

    reg {
        regwidth = 64;
        accesswidth = 32;
    } reg_b @ 0x08; // OK. "Wide" register of 64-bits, but is accessed using 32-bit subwords

    reg {
        regwidth = 8;
        accesswidth = 8;
    } reg_c @ 0x10; // OK. Is aligned to the cpuif bus width

    reg {
        regwidth = 32;
        accesswidth = 8;
    } bad_reg @ 0x14; // NOT OK. accesswidth conflicts with cpuif width
