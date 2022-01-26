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