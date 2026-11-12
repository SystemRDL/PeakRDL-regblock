Hardware Interface
------------------

The generated register block will present the entire hardware interface to the user
using two struct ports:

* ``hwif_in``
* ``hwif_out``

All field inputs and outputs as well as signals are consolidated into these
struct ports. The presence of each depends on the specific contents of the design
being exported.


Struct type names
~~~~~~~~~~~~~~~~~

The generated package declares the top-level hardware interface structs using
the addrmap's RDL type name:

* ``<addrmap_type_name>__in_t``
* ``<addrmap_type_name>__out_t``

The elaborated instance name and generated module name do not affect these
typedef names. This allows a reusable addrmap type to be exported under
different instance or module names while retaining a stable hardware interface
type name. Addrmap type parameters also do not change these names.

For example, exporting the ``my_sub`` addrmap as an instance named ``regblock``
produces ``my_sub__in_t`` and ``my_sub__out_t`` in the generated package, while
the module ports are still named ``hwif_in`` and ``hwif_out``.

The ``--type-style`` option controls how nested struct type names are generated.
The top-level struct typedefs always follow the addrmap type name. If the top
addrmap is anonymous or imported without type information, the exporter falls
back to a generated type name or the instance name.


Using structs for the hardware interface has the following benefits:

* Preserves register map component grouping, arrays, and hierarchy.
* Avoids naming collisions and cumbersome signal name flattening.
* Allows for more natural mapping and distribution of register block signals to a design's hardware components.
* Use of unpacked arrays/structs prevents common assignment mistakes as they are enforced by the compiler.


Structs are organized as follows: ``hwif_out.<heir_path>.<feature>``

For example, a simple design such as:

.. code-block:: systemrdl

        addrmap my_design {
            reg {
                field {
                    sw = rw;
                    hw = rw;
                    we;
                } my_field;
            } my_reg[2];
        };

... results in the following struct members:

.. code-block:: text

    hwif_out.my_reg[0].my_field.value
    hwif_in.my_reg[0].my_field.next
    hwif_in.my_reg[0].my_field.we
    hwif_out.my_reg[1].my_field.value
    hwif_in.my_reg[1].my_field.next
    hwif_in.my_reg[1].my_field.we

For brevity in this documentation, hwif features will be described using shorthand
notation that omits the hierarchical path: ``hwif_out..<feature>``


.. important::

    The PeakRDL tool makes no guarantees on the field order of the hwif structs.
    For this reason, it is strongly recommended to always access struct members
    directly, by name.

    If using the SystemVerilog streaming operator to assign the hwif struct to a
    packed vector, be extremely careful to avoid assumptions on the resulting bit-position of a field.
