Signal Properties
=================

.. note:: Any properties not explicitly listed here are either implicitly
    supported, or are not relevant to the regblock exporter and are ignored.


activehigh/activelow
--------------------
Only relevant for signals used as resets. Defines the reset signal's polarity.


sync/async
----------
Only supported for signals used as resets to infer edge-sensitive reset.
Ignored in all other contexts.


cpuif_reset
-----------
Specify that this signal shall be used as alternate reset signal for the CPU
interface for this regblock.


field_reset
-----------
Specify that this signal is used as an alternate reset signal for all fields
instantiated in sub-hierarchies relative to this signal.
