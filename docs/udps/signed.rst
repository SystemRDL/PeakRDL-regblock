.. _signed:

Signed Fields
=============

SystemRDL does not natively provide a way to mark fields as signed or unsigned.
The ``is_signed`` user-defined property fills this need.

For this SystemVerilog exporter, marking a field as signed only affects the
signal type in the ``hwif`` structs. There is no special handling in the internals
of the regblock.

Properties
----------
A field can be marked as signed using the following user-defined property:

.. literalinclude:: ../../hdl-src/regblock_udps.rdl
    :lines: 40-44

This UDP definition, along with others supported by PeakRDL-regblock, can be
enabled by compiling the following file along with your design:
:download:`regblock_udps.rdl <../../hdl-src/regblock_udps.rdl>`.

.. describe:: is_signed

    *   Assigned value is a boolean.
    *   If true, the hardware interface field will have the type
        ``logic signed [width-1:0]``.
    *   If false or not defined for a field, the hardware interface field will
        have the type ``logic [width-1:0]``, which is unsigned by definition.

Other Rules
^^^^^^^^^^^

*   ``is_signed=true`` is mutually exclusive with the ``counter`` property.
*   ``is_signed=true`` is mutually exclusive with the ``encode`` property.

Examples
--------
Below are some examples of fields with different signedness.

Signed Fields
^^^^^^^^^^^^^
.. code-block:: systemrdl
    :emphasize-lines: 3, 8

    field {
        sw=rw; hw=r;
        is_signed;
    } signed_num[63:0] = 0;

    field {
        sw=r; hw=w;
        is_signed = true;
    } another_signed_num[19:0] = 20'hFFFFF; // -1

SystemRDL's own integer type is always unsigned. In order to specify a negative
reset value, the two's complement value must be used as shown in the second
example above.

Unsigned Fields
^^^^^^^^^^^^^^^
.. code-block:: systemrdl
    :emphasize-lines: 3, 8

    field {
        sw=rw; hw=r;
        // fields are unsigned by default
    } unsigned_num[63:0] = 0;

    field {
        sw=r; hw=w;
        is_signed = false;
    } another_unsigned_num[19:0] = 0;
