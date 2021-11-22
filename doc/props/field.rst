Field Properties
================

.. note:: Any properties not explicitly listed here are either implicitly supported,
    or are not relevant to the regblock exporter and are ignored.

Software Access Properties
--------------------------

onread/onwrite
^^^^^^^^^^^^^^
|EX|

rclr/rset
^^^^^^^^^
See ``onread``

singlepulse
^^^^^^^^^^^
|NO|

sw
^^^
|OK|

swacc
^^^^^
|EX|

If true, infers an output signal ``swacc`` that is asserted as the field is sampled for a software read operation.

.. wavedrom::

    {signal: [
        {name: 'clk',             wave: 'p....'},
        {name: 'hwif_in..value',  wave: 'x.=x.', data: ['D']},
        {name: 'hwif_out..swacc', wave: '0.10.'}
    ]}


swmod
^^^^^
|EX|

If true, infers an output signal ``swmod`` that is asserted as the field is being modified by software.

.. wavedrom::

    {signal: [
        {name: 'clk',             wave: 'p.....'},
        {name: 'hwif_out..value', wave: '=..=..', data: ['old', 'new']},
        {name: 'hwif_out..swmod', wave: '0.10..'}
    ]}


swwe/swwel
^^^^^^^^^^

TODO: Describe result

boolean
    |NO|

bit
    |NO|

reference
    |NO|

woclr/woset
^^^^^^^^^^^
See ``onwrite``


Hardware Access Properties
--------------------------

anded/ored/xored
^^^^^^^^^^^^^^^^
|EX|


hw
^^^
|OK|

hwclr/hwset
^^^^^^^^^^^
boolean
    |EX|

reference
    |EX|

hwenable/hwmask
^^^^^^^^^^^^^^^
|EX|

we/wel
^^^^^^
Write-enable control from hardware interface

.. wavedrom::

    {signal: [
        {name: 'clk',             wave: 'p....'},
        {name: 'hwif_in..value',  wave: 'x.=x.', data: ['D']},
        {name: 'hwif_in..we',     wave: '0.10.',},
        {name: 'hwif_in..wel',    wave: '1.01.',},
        {name: '<field value>',   wave: 'x..=.', data: ['D']}
    ]}

boolean
    |OK|

    if set, infers the existence of input signal ``hwif_in..we`` or ``hwif_in..wel``

reference
    |EX|


Counter Properties
------------------

counter
^^^^^^^
|NO|

decr
^^^^
reference
    |NO|

decrthreshold
^^^^^^^^^^^^^
boolean
    |NO|

bit
    |NO|

reference
    |NO|

decrsaturate
^^^^^^^^^^^^
boolean
    |NO|

bit
    |NO|

reference
    |NO|

decrvalue
^^^^^^^^^
bit
    |NO|

reference
    |NO|

decrwidth
^^^^^^^^^
|NO|

incr
^^^^
|NO|

incrsaturate/saturate
^^^^^^^^^^^^^^^^^^^^^
boolean
    |NO|

bit
    |NO|

reference
    |NO|

incrthreshold/threshold
^^^^^^^^^^^^^^^^^^^^^^^
boolean
    |NO|

bit
    |NO|

reference
    |NO|

incrvalue
^^^^^^^^^
bit
    |NO|

reference
    |NO|

incrwidth
^^^^^^^^^
|NO|

overflow
^^^^^^^^
|NO|

underflow
^^^^^^^^^
|NO|


Interrupt Properties
--------------------

enable
^^^^^^
|NO|

haltenable
^^^^^^^^^^
|NO|

haltmask
^^^^^^^^
|NO|

intr
^^^^
|NO|

mask
^^^^
|NO|

sticky
^^^^^^
|NO|

stickybit
^^^^^^^^^
|NO|


Misc
----

encode
^^^^^^
|NO|

next
^^^^
|NO|

paritycheck
^^^^^^^^^^^
|NO|

precedence
^^^^^^^^^^
|EX|

reset
^^^^^
bit
    |OK|

reference
    |EX|

resetsignal
^^^^^^^^^^^
|EX|
