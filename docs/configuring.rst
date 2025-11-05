.. _peakrdl_cfg:

Configuring PeakRDL-regblock
============================

If using the `PeakRDL command line tool <https://peakrdl.readthedocs.io/>`_,
some aspects of the ``regblock`` command have additional configuration options
available via the PeakRDL TOML file.

All regblock-specific options are defined under the ``[regblock]`` TOML heading.

.. data:: cpuifs

    Mapping of additional CPU Interface implementation classes to load.
    The mapping's key indicates the cpuif's name.
    The value is a string that describes the import path and cpuif class to
    load.

    For example:

    .. code-block:: toml

        [regblock]
        cpuifs.my-cpuif-name = "my_cpuif_module:MyCPUInterfaceClass"


.. data:: default_reset

    Choose the default style of reset signal if not explicitly
    specified by the SystemRDL design. If unspecified, the default reset
    is active-high and synchronous.

    Choice of:

        * ``rst`` (default)
        * ``rst_n``
        * ``arst``
        * ``arst_n``

    For example:

    .. code-block:: toml

        [regblock]
        default_reset = "arst"

.. data:: err_if_bad_addr

    If set to true, generate CPUIF error response if a transaction attempts to
    access an address that does not map to anything.

.. data:: err_if_bad_rw

    If set to true, generate CPUIF error response if an illegal access is
    performed to a read-only or write-only register.
