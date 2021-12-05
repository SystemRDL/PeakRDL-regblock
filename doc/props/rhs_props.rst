RHS Property References
=======================

SystemRDL allows some properties to be referenced in the righthand-side of
property assignment expressions:

    .. code-block:: systemrdl

            some_property = my_reg.my_field->some_property;

The official SystemRDL spec refers to these as "Ref targets" in Table G1, but
unfortunately does not describe their semantics in much detail.

The text below describes the interpretations used for this exporter.

--------------------------------------------------------------------------------

Field
-----

swacc
^^^^^
|EX|

Single-cycle strobe that indicates the field is being sampled during a software
read operation.


swmod
^^^^^
|EX|

Single-cycle strobe that indicates the field is being modified during a software
access operation.


swwe/swwel
^^^^^^^^^^
|OK|

Represents the signal that controls the owning field's swwe/swwel behavior.


anded/ored/xored
^^^^^^^^^^^^^^^^
|EX|

Represents the current and/or/xor reduction of the owning field's value.


hwclr/hwset
^^^^^^^^^^^
|EX|

Represents the signal that controls the owning field's hwclr/hwset behavior.


hwenable/hwmask
^^^^^^^^^^^^^^^
|EX|

Represents the signal that controls the owning field's hwenable/hwmask behavior.

we/wel
^^^^^^
|EX|

next
^^^^
|EX|

reset
^^^^^
|EX|

resetsignal
^^^^^^^^^^^
|EX|

--------------------------------------------------------------------------------

Field Counter Properties
------------------------

Represents the signal that controls the owning field's we/wel behavior.

decr
^^^^
|NO|

decrthreshold
^^^^^^^^^^^^^
|NO|

decrsaturate
^^^^^^^^^^^^
|NO|

decrvalue
^^^^^^^^^
|EX|

incr
^^^^
|NO|

incrsaturate/saturate
^^^^^^^^^^^^^^^^^^^^^
|NO|

incrthreshold/threshold
^^^^^^^^^^^^^^^^^^^^^^^
|NO|

incrvalue
^^^^^^^^^
|EX|

overflow
^^^^^^^^
|NO|

underflow
^^^^^^^^^
|NO|

--------------------------------------------------------------------------------

Field Interrupt Properties
--------------------------

enable
^^^^^^
|EX|

haltenable
^^^^^^^^^^
|EX|

haltmask
^^^^^^^^
|EX|

mask
^^^^
|EX|


--------------------------------------------------------------------------------

Register
--------

intr
^^^^
|NO|

halt
^^^^
|NO|
