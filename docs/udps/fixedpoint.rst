.. _fixedpoint:

Signed and Fixedpoint Fields
============================

SystemRDL does not natively provide a way to mark fields as signed or unsigned.
The ``is_signed`` user-defined property fills this need. Similarly, the
``fracwidth`` and ``intwidth`` user-defined properties can be used to declare
the fixedpoint representation of a field.

For this SystemVerilog exporter, these properties only affect the signal type in
the the ``hwif`` structs. There is no special handling in the internals of
the regblock.

Properties
----------
The behavior of signed and/or fixedpoint fields is defined using the following
three properties:

.. literalinclude:: ../../hdl-src/regblock_udps.rdl
    :lines: 40-54

These UDP definitions, along with others supported by PeakRDL-regblock can be
enabled by compiling the following file along with your design:
:download:`regblock_udps.rdl <../../hdl-src/regblock_udps.rdl>`.

.. describe:: is_signed

    *   Assigned value is a boolean.
    *   If true, the hardware interface field will have the
        ``logic signed [width-1:0]`` type.
    *   If false, the hardware interface field will have the
        ``logic unsigned [width-1:0]`` type.
    *   If not defined for a field, the field will have the ``logic [width-1:0]``
        type.

.. describe:: intwidth

    *   The ``intwidth`` property defines the number of integer bits in the
        fixedpoint representation (including the sign bit, if present).
    *   If ``intwidth`` is defined for a field and ``is_signed`` is not,
        ``is_signed`` is inferred as false (unsigned).
    *   If ``is_signed`` is true, the fixedpoint representation has a range from
        :math:`-2^{\mathrm{intwidth}-1}` to :math:`2^{\mathrm{intwidth}-1} -2^{-\mathrm{fracwidth}}`.
    *   If ``is_signed`` is false, the fixedpoint representation has a range from
        :math:`0` to :math:`2^{\mathrm{intwidth}} - 2^{-\mathrm{fracwidth}}`.
    *   The type of the field in the ``hwif`` struct is
        ``logic (un)signed [intwidth-1:-fracwidth]``.

.. describe:: fracwidth

    *   The ``fracwidth`` property defines the number of fractional bits in the
        fixedpoint representation.
    *   The weight of the least significant bit of the field is
        :math:`2^{-\mathrm{fracwidth}}`.
    *   If ``fracwidth`` is defined for a field and ``is_signed`` is not,
        ``is_signed`` is inferred as false (unsigned).
    *   The type of the field in the ``hwif`` struct is
        ``logic (un)signed [intwidth-1:-fracwidth]``.

Other Rules
^^^^^^^^^^^
*   Only one of ``fracwidth`` or ``intwidth`` need be defined. The other is
    inferred from the field bit width.
*   The bit width of the field shall be equal to ``fracwidth`` + ``intwidth``.
*   If both ``intwidth`` and ``fracwidth`` are defined for a field,  it is an
    error if their sum does not equal the bit width of the field.
*   Either ``fracwidth`` or ``intwidth`` can be a negative integer. Because
    SystemRDL does not have a signed integer type, the only way to achieve
    this is to define one of the widths as larger than the bit width of the
    component so that the other width is inferred as a negative number.
*   The properties defined above are mutually exclusive with the ``counter``
    property (with the exception of ``is_signed=false``).
*   The properties defined above are mutually exclusive with the ``encode``
    property.
