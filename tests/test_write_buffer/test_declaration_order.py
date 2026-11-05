"""
Regression: declaration order of the field storage struct.

A ``wbuffer_trigger`` may name a field (``singlepulse``) or a propref such as
``anded``. ``WriteBuffering.get_raw_trigger()`` dereferences it to
``field_storage.<path>.value``, so the write-buffer implementation reads
``field_storage``. IEEE 1800 requires data to be declared before it is used,
so the field storage struct has to be emitted ahead of the write buffers.

This test inspects the generated SystemVerilog and needs no simulator.
"""

import os
import pathlib

from systemrdl import RDLCompiler

from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.cpuif.passthrough import PassthroughCpuif
from peakrdl_regblock.udps import ALL_UDPS

TEST_DIR = pathlib.Path(__file__).parent
RDL_FILE = TEST_DIR / "regblock.rdl"
UDP_FILE = TEST_DIR.parent.parent / "hdl-src" / "regblock_udps.rdl"

STORAGE_DECL = "field_storage_t field_storage;"


def _export_regblock(output_dir: pathlib.Path) -> str:
    rdlc = RDLCompiler()
    for udp in ALL_UDPS:
        rdlc.register_udp(udp)
    rdlc.compile_file(str(UDP_FILE))
    rdlc.compile_file(str(RDL_FILE))
    root = rdlc.elaborate(None, "regblock")

    RegblockExporter().export(
        root,
        str(output_dir),
        module_name="regblock",
        package_name="regblock_pkg",
        cpuif_cls=PassthroughCpuif,
    )

    return os.path.join(str(output_dir), "regblock.sv")


def test_field_storage_declared_before_use(tmp_path):
    module_path = _export_regblock(tmp_path)
    with open(module_path, "r", encoding="utf-8") as f:
        text = f.read()

    assert STORAGE_DECL in text, "expected the field storage struct to be declared"

    # Every read of the struct (there is at least one, in a write-buffer
    # always_ff block) must follow the declaration.
    first_use = text.find("field_storage.")
    assert first_use != -1, "expected field_storage to be referenced"

    decl = text.find(STORAGE_DECL)
    assert decl < first_use, (
        "field_storage is used before it is declared\n"
        f"  declaration at offset {decl}\n"
        f"  first use at offset {first_use}\n"
        "Declare field storage before the write-buffer implementation."
    )
