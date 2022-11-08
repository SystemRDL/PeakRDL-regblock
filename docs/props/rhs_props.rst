RHS Property References
=======================

SystemRDL allows some properties to be referenced in the righthand-side of
property assignment expressions:

    .. code-block:: systemrdl

            some_property = my_reg.my_field -> some_property;

The official SystemRDL spec refers to these as "Ref targets" in Table G1, but
unfortunately does not describe their semantics in much detail.

The text below describes the interpretations used for this exporter.

--------------------------------------------------------------------------------

Field
-----

field -> swacc
^^^^^^^^^^^^^^
|EX|

Single-cycle strobe that indicates the field is being accessed by software
(read or write).


field -> swmod
^^^^^^^^^^^^^^^
|EX|

Single-cycle strobe that indicates the field is being modified during a software
access operation.


field -> swwe/swwel
^^^^^^^^^^^^^^^^^^^
|OK|

Represents the signal that controls the field's swwe/swwel behavior.


field -> anded/ored/xored
^^^^^^^^^^^^^^^^^^^^^^^^^
|EX|

Represents the current and/or/xor reduction of the field's value.


field -> hwclr/hwset
^^^^^^^^^^^^^^^^^^^^
|EX|

Represents the signal that controls the field's hwclr/hwset behavior.


field -> hwenable/hwmask
^^^^^^^^^^^^^^^^^^^^^^^^
|EX|

Represents the signal that controls the field's hwenable/hwmask behavior.

field -> we/wel
^^^^^^^^^^^^^^^
|EX|

Represents the signal that controls the field's we/wel behavior.

field -> next
^^^^^^^^^^^^^
|EX|

field -> reset
^^^^^^^^^^^^^^
|EX|

field -> resetsignal
^^^^^^^^^^^^^^^^^^^^
|EX|

--------------------------------------------------------------------------------

Field Counter Properties
------------------------

field -> incr
^^^^^^^^^^^^^
|EX|

Represents the signal that controls the field's counter increment control.

field -> incrsaturate/saturate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
|EX|

Represents the internal 1-bit event signal that indicates whether the counter is saturated
at its saturation value.

.. wavedrom::

    {
        "signal": [
            {"name": "clk",            "wave": "p......"},
            {"name": "hwif_in..decr",  "wave": "0101010"},
            {"name": "<counter>",      "wave": "=.=....", "data": [1,0]},
            {"name": "<decrsaturate>", "wave": "0.1...."}
        ],
        "foot": {
            "text": "A 4-bit counter saturating"
        }
    }


field -> incrthreshold/threshold
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
|EX|

Represents the 1-bit event signal that indicates whether the counter has met or
exceeded its incrthreshold.

field -> incrvalue
^^^^^^^^^^^^^^^^^^
|EX|

Represents the value that was assigned to this property.

field -> overflow
^^^^^^^^^^^^^^^^^
|OK|

Represents the event signal that is asserted when the counter is about to wrap.

field -> decr
^^^^^^^^^^^^^
|EX|

Represents the signal that controls the field's counter decrement control.

field -> decrsaturate
^^^^^^^^^^^^^^^^^^^^^
|EX|

Represents the internal 1-bit event signal that indicates whether the counter is saturated
at its saturation value.

.. wavedrom::

    {
        "signal": [
            {"name": "clk",            "wave": "p......"},
            {"name": "hwif_in..incr",  "wave": "0101010"},
            {"name": "<counter>",      "wave": "=.=....", "data": [14,15]},
            {"name": "<incrsaturate>", "wave": "0.1...."}
        ],
        "foot": {
            "text": "A 4-bit counter saturating"
        }
    }

field -> decrthreshold
^^^^^^^^^^^^^^^^^^^^^^
|EX|

Represents the 1-bit event signal that indicates whether the counter has met or
exceeded its incrthreshold.

field -> decrvalue
^^^^^^^^^^^^^^^^^^
|EX|

Represents the value that was assigned to this property.

field -> underflow
^^^^^^^^^^^^^^^^^^
|OK|

Represents the event signal that is asserted when the counter is about to wrap.

--------------------------------------------------------------------------------

Field Interrupt Properties
--------------------------

field -> enable
^^^^^^^^^^^^^^^
|EX|

field -> mask
^^^^^^^^^^^^^
|EX|

field -> haltenable
^^^^^^^^^^^^^^^^^^^
|EX|

field -> haltmask
^^^^^^^^^^^^^^^^^
|EX|


--------------------------------------------------------------------------------

Register
--------

reg -> intr
^^^^^^^^^^^
|OK|

References the register's ``hwif_out..intr`` signal.

reg -> halt
^^^^^^^^^^^
|OK|

References the register's ``hwif_out..halt`` signal.
