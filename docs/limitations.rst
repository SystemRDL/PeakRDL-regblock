Known Issues & Limitations
==========================

Not all SystemRDL features are supported by this exporter. For a listing of
supported properties, see the appropriate property listing page in the following
sections.


External Components
-------------------
Regfiles, registers & fields instantiated using the ``external`` keyword are not supported yet.


Alias Registers
---------------
Registers instantiated using the ``alias`` keyword are not supported yet.


Unaligned Registers
-------------------
All address offsets & strides shall be a multiple of the regwidth used. Specifically:

* Each register's address and array stride shall be aligned to it's regwidth.
* Each regfile or addrmap shall use an offset and stride that is a multiple of the largest regwidth it encloses.


No partial writes
-----------------

Some protocols describe byte-level write strobes. These are not supported yet.
All write transfers must access the entire register width.


Register width, Access width and CPUIF bus width
------------------------------------------------
To keep the initial architecture simpler, currently ``regwidth``, ``accesswidth``
and the resulting CPU bus width has some limitations:

* All registers shall have ``regwidth`` == ``accesswidth``
* ``regwidth`` shall be the same across all registers within the block being exported.
* The CPU interface's bus width is statically determined by the ``regwidth`` used.

I have plans to remove these restrictions and allow for more flexibility in the future.
