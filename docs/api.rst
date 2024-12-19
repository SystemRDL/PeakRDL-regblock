Exporter API
============

If you are not using the `PeakRDL command-line tool <https://peakrdl.readthedocs.io>`_,
you can still generate regblocks programmatically using the exporter API:

.. autoclass:: peakrdl_regblock.RegblockExporter
    :members:

Example
-------
Below is a simple example that demonstrates how to generate a SystemVerilog
implementation from SystemRDL source.

.. code-block:: python
    :emphasize-lines: 2-4, 29-33

    from systemrdl import RDLCompiler, RDLCompileError
    from peakrdl_regblock import RegblockExporter
    from peakrdl_regblock.cpuif.axi4lite import AXI4Lite_Cpuif
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
        cpuif_cls=AXI4Lite_Cpuif
    )
