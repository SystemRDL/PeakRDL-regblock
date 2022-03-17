Hardware Interface
------------------

The generated register block will present the entire hardware interface to the user
using two struct ports:

* ``hwif_in``
* ``hwif_out``

All field inputs and outputs as well as signals are consolidated into these
struct ports. The presence of each depends on the specific contents of the design
being exported.


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
