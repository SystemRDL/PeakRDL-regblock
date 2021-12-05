Field Properties
================

.. note:: Any properties not explicitly listed here are either implicitly
    supported, or are not relevant to the regblock exporter and are ignored.

Software Access Properties
--------------------------

onread/onwrite
^^^^^^^^^^^^^^
|OK|

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
|OK|

If true, infers an output signal ``hwif_out..swacc`` that is asserted on the
same clock cycle that the field is being sampled during a software read
operation.

.. wavedrom::

    {signal: [
        {name: 'clk',             wave: 'p....'},
        {name: 'hwif_in..value',  wave: 'x.=x.', data: ['D']},
        {name: 'hwif_out..swacc', wave: '0.10.'}
    ]}


swmod
^^^^^
|OK|

If true, infers an output signal ``hwif_out..swmod`` that is asserted as the
field is being modified by software.

.. wavedrom::

    {signal: [
        {name: 'clk',             wave: 'p.....'},
        {name: 'hwif_out..value', wave: '=..=..', data: ['old', 'new']},
        {name: 'hwif_out..swmod', wave: '0.10..'}
    ]}


swwe/swwel
^^^^^^^^^^

Provides a mechanism that allows hardware to override whether the field is
writable by software.

boolean
    |OK|

    If True, infers an input signal ``hwif_in..swwe`` or ``hwif_in..swwel``.

reference
    |OK|


woclr/woset
^^^^^^^^^^^
See ``onwrite``


--------------------------------------------------------------------------------

Hardware Access Properties
--------------------------

anded/ored/xored
^^^^^^^^^^^^^^^^
|OK|

If true, infers the existence of output signal: ``hwif_out..anded``,
``hwif_out..ored``, ``hwif_out..xored``


hw
^^^
|OK|

hwclr/hwset
^^^^^^^^^^^

If both ``hwclr`` and ``hwset`` properties are used, and both are asserted at
the same clock cycle, then ``hwset`` will take precedence.

boolean
    |OK|

    If true, infers the existence of input signal: ``hwif_in..hwclr``, ``hwif_in..hwset``

reference
    |OK|

hwenable/hwmask
^^^^^^^^^^^^^^^
|OK|

we/wel
^^^^^^
Write-enable control from hardware interface.

If true, infers the existence of input signal: ``hwif_in..we``, ``hwif_in..wel``

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

    If true, infers the existence of input signal ``hwif_in..we`` or ``hwif_in..wel``

reference
    |OK|


--------------------------------------------------------------------------------

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


--------------------------------------------------------------------------------

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


--------------------------------------------------------------------------------

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
