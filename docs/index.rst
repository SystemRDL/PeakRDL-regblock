Introduction
============

PeakRDL-regblock is a free and open-source control & status register (CSR) compiler.
This code generator translates your SystemRDL register description into
a synthesizable SystemVerilog RTL module that can be easily instantiated into
your hardware design.

* Generates fully synthesizable SystemVerilog RTL (IEEE 1800-2012)
* Options for many popular CPU interface protocols (AMBA APB, AXI4-Lite, and more)
* Configurable pipelining options for designs with fast clock rates.
* Broad support for SystemRDL 2.0 features
* Fully synthesizable SystemVerilog. Tested on Xilinx/AMD's Vivado & Intel Quartus

.. warning::

    The PeakRDL-regblock SV generator is still in pre-production (v0.x version numbers).
    During this time, I may decide to refactor things which could break compatibility.


Installing
----------

Install from `PyPi`_ using pip

.. code-block:: bash

    python3 -m pip install peakrdl-regblock

.. _PyPi: https://pypi.org/project/peakrdl-regblock



Quick Start
-----------

Below is a simple example that demonstrates how to generate a SystemVerilog
implementation from SystemRDL source.

.. code-block:: python
    :emphasize-lines: 2-4, 29-33

    from systemrdl import RDLCompiler, RDLCompileError
    from peakrdl_regblock import RegblockExporter
    from peakrdl_regblock.cpuif.apb3 import APB3_Cpuif
    from peakrdl_regblock.udps import ALL_UDPS

    input_files = [
        "PATH/TO/my_register_block.rdl"
    ]

    # Create an instance of the compiler
    rdlc = RDLCompiler()

    # Register all UDPs that 'regblock' requires
    for udp in ALL_UDPS:
        rdlc.register_udp(udp)

    try:
        # Compile your RDL files
        for input_file in input_files:
            rdlc.compile_file(input_file)

        # Elaborate the design
        root = rdlc.elaborate()
    except RDLCompileError:
        # A compilation error occurred. Exit with error code
        sys.exit(1)

    # Export a SystemVerilog implementation
    exporter = RegblockExporter()
    exporter.export(
        root, "path/to/output_dir",
        cpuif_cls=APB3_Cpuif
    )


Links
-----

- `Source repository <https://github.com/SystemRDL/PeakRDL-regblock>`_
- `Release Notes <https://github.com/SystemRDL/PeakRDL-regblock/releases>`_
- `Issue tracker <https://github.com/SystemRDL/PeakRDL-regblock/issues>`_
- `PyPi <https://pypi.org/project/peakrdl-regblock>`_
- `SystemRDL Specification <http://accellera.org/downloads/standards/systemrdl>`_



.. toctree::
    :hidden:

    self
    architecture
    hwif
    api
    limitations

.. toctree::
    :hidden:
    :caption: CPU Interfaces

    cpuif/introduction
    cpuif/apb
    cpuif/axi4lite
    cpuif/passthrough
    cpuif/internal_protocol
    cpuif/customizing

.. toctree::
    :hidden:
    :caption: Property Support

    props/field
    props/reg
    props/addrmap
    props/signal
    props/rhs_props

.. toctree::
    :hidden:
    :caption: Extended Properties

    udps/intro
    udps/read_buffering
    udps/write_buffering
