Customizing the CPU interface
=============================

Use your own existing SystemVerilog interface definition
--------------------------------------------------------

This exporter comes pre-bundled with its own SystemVerilog interface declarations.
What if you already have your own SystemVerilog interface declaration that you prefer?

Not a problem! As long as your interface definition is similar enough, it is easy
to customize and existing CPUIF definition.


As an example, let's use the SystemVerilog interface definition for
:ref:`cpuif_axi4lite` that is bundled with this project. This interface uses
the following style and naming conventions:

* SystemVerilog interface type name is ``axi4lite_intf``
* Defines modports named ``master`` and ``slave``
* Interface signals are all upper-case: ``AWREADY``, ``AWVALID``, etc...

Lets assume your preferred SV interface definition uses a slightly different naming convention:

* SystemVerilog interface type name is ``axi4_lite_interface``
* Modports are capitalized and use suffixes ``Master_mp`` and ``Slave_mp``
* Interface signals are all lower-case: ``awready``, ``awvalid``, etc...

Rather than rewriting a new CPU interface definition, you can extend and adjust the existing one:

.. code-block:: python

    from peakrdl_regblock.cpuif.axi4lite import AXI4Lite_Cpuif

    class My_AXI4Lite(AXI4Lite_Cpuif):
        @property
        def port_declaration(self) -> str:
            # Override the port declaration text to use the alternate interface name and modport style
            return "axi4_lite_interface.Slave_mp s_axil"

        def signal(self, name:str) -> str:
            # Override the signal names to be lowercase instead
            return "s_axil." + name.lower()

Then use your custom CPUIF during export:

.. code-block:: python

   exporter = RegblockExporter()
   exporter.export(
      root, "path/to/output_dir",
      cpuif_cls=My_AXI4Lite
   )



Custom CPU Interface Protocol
-----------------------------

If you require a CPU interface protocol that is not included in this project,
you can define your own.

1. Create a SystemVerilog CPUIF implementation template file.

    This contains the SystemVerilog implementation of the bus protocol. The logic
    in this shall implement a translation between your custom protocol and the
    :ref:`cpuif_protocol`.

    Reminder that this template will be preprocessed using Jinja, so you can use
    some templating tags to dynamically render content. See the implementations of
    existing CPU interfaces as an example.

2. Create a Python class that defines your CPUIF

    Extend your class from :class:`peakrdl_regblock.cpuif.CpuifBase`.
    Define the port declaration string, and provide a reference to your template file.

3. Use your new CPUIF definition when exporting.
4. If you think the CPUIF protocol is something others might find useful, let me know and I can add it to PeakRDL!
