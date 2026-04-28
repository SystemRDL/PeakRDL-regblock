"""Unit tests for the bytewise-parity scanner population in DesignState."""
import os
from systemrdl import RDLCompiler
from systemrdl.messages import MessagePrinter, Severity
from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.udps import ALL_UDPS


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class _CountingPrinter(MessagePrinter):
    """MessagePrinter that records messages by severity for assertion in tests."""
    def __init__(self):
        super().__init__()
        self.warnings = []  # list of message strings
        self.errors = []

    def emit_message(self, lines):
        # Don't actually print to stderr — keep test output clean.
        pass

    def print_message(self, severity, text, src_ref):
        if severity == Severity.WARNING:
            self.warnings.append(text)
        elif severity in (Severity.ERROR, Severity.FATAL):
            self.errors.append(text)
        # swallow output


def _elaborate(rdl_relpath: str, message_printer=None):
    if message_printer is not None:
        rdlc = RDLCompiler(message_printer=message_printer)
    else:
        rdlc = RDLCompiler()
    for udp in ALL_UDPS:
        rdlc.register_udp(udp)
    rdlc.compile_file(os.path.join(REPO_ROOT, "hdl-src/regblock_udps.rdl"))
    rdlc.compile_file(os.path.join(REPO_ROOT, rdl_relpath))
    return rdlc.elaborate()


def test_bytewise_off_leaves_collections_empty(tmp_path):
    root = _elaborate("tests/test_parity/regblock.rdl")
    e = RegblockExporter()
    e.export(root, str(tmp_path), module_name="regblock", package_name="regblock_pkg")
    assert e.ds.bytewise_parity is False
    assert e.ds.has_bytewise_parity is False
    assert e.ds.parity_fields == []
    assert e.ds.parity_bits == []


def test_bytewise_on_collects_all_storage_fields(tmp_path):
    # test_parity/regblock.rdl has fields: f1[16], f2[8], f3[1] in 1 + 8 = 9 reg instances.
    root = _elaborate("tests/test_parity/regblock.rdl")
    e = RegblockExporter()
    e.export(
        root, str(tmp_path),
        module_name="regblock", package_name="regblock_pkg",
        bytewise_parity=True,
    )
    assert e.ds.has_bytewise_parity is True
    # 3 fields per reg instance, 9 reg instances total = 27 fields
    assert len(e.ds.parity_fields) == 27

    # f1 is 16 bits = 2 parity bytes; f2 is 8 bits = 1; f3 is 1 bit = 1.
    # Per reg: 2 + 1 + 1 = 4 parity bits. 9 regs = 36 parity bits.
    assert len(e.ds.parity_bits) == 36


def test_bytewise_byte_count_for_widths(tmp_path):
    """Verify ceil(W/8) byte-count rule for the canonical widths."""
    root = _elaborate("tests/test_parity/regblock.rdl")
    e = RegblockExporter()
    e.export(
        root, str(tmp_path),
        module_name="regblock", package_name="regblock_pkg",
        bytewise_parity=True,
    )

    widths_seen = sorted({node.width for (node, _bc, _f, _p) in e.ds.parity_fields})
    assert widths_seen == [1, 8, 16]

    for (node, byte_count, ferr_idx, first_pinj_idx) in e.ds.parity_fields:
        assert byte_count == (node.width + 7) // 8


def test_paritycheck_with_bytewise_emits_warning(tmp_path):
    """When --parity-byte is on AND a field has paritycheck=true, the scanner
    must warn so users know the property is redundant in this mode."""
    printer = _CountingPrinter()
    # tests/test_parity/regblock.rdl has `default paritycheck;` so every field is tagged.
    root = _elaborate("tests/test_parity/regblock.rdl", message_printer=printer)
    initial = len(printer.warnings)

    e = RegblockExporter()
    e.export(
        root, str(tmp_path),
        module_name="regblock", package_name="regblock_pkg",
        bytewise_parity=True,
    )
    final = len(printer.warnings)
    assert final > initial, (
        "Expected at least one warning when paritycheck and --parity-byte are both on; "
        f"warning count went {initial} -> {final}"
    )
    # Sanity: the new warning text mentions --parity-byte
    new_warnings = printer.warnings[initial:]
    assert any("--parity-byte" in w for w in new_warnings), (
        f"Expected the redundancy warning to mention --parity-byte, got: {new_warnings}"
    )


def test_paritycheck_alone_no_redundancy_warning(tmp_path):
    """Sanity: legacy mode with paritycheck and reset values defined should not
    emit the new redundancy warning."""
    printer = _CountingPrinter()
    root = _elaborate("tests/test_parity/regblock.rdl", message_printer=printer)
    initial = len(printer.warnings)

    e = RegblockExporter()
    e.export(
        root, str(tmp_path),
        module_name="regblock", package_name="regblock_pkg",
        # bytewise_parity defaults to False
    )
    # All fields in the test RDL have explicit reset values, so the legacy
    # "missing reset" warning should not fire either.
    assert len(printer.warnings) == initial, (
        f"Unexpected warnings in legacy mode: "
        f"{initial} -> {len(printer.warnings)}: {printer.warnings[initial:]}"
    )
