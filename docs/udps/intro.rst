Introduction
============

Although the official SystemRDL spec defines numerous properties that allow you
to define complex register map structures, sometimes they are not enough to
accurately describe a necessary feature. Fortunately the SystemRDL spec allows
the language to be extended using "User Defined Properties" (UDPs). The
PeakRDL-regblock tool understands several UDPs that are described in this
section.


.. list-table:: Summary of UDPs
    :header-rows: 1

    *   - Name
        - Component
        - Type
        - Description

    *   - buffer_writes
        - reg
        - boolean
        - If set, writes to the register are double-buffered.

          See details here: :ref:`write_buffering`.

    *   - wbuffer_trigger
        - reg
        - reference
        - Defines the buffered write commit trigger.

          See details here: :ref:`write_buffering`.
