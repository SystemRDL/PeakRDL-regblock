# Byte-wise Per-Field Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add CLI-flag-driven byte-wise per-field parity protection to PeakRDL-regblock, plus an orthogonal `--odd-parity` polarity flag, both additive to the existing `paritycheck` RDL property path.

**Architecture:** Two new CLI flags on the `peakrdl regblock` subcommand. `--odd-parity` is a small inverter applied to whatever parity is generated (legacy or new path). `--parity-byte` enables a new byte-wise per-field parity architecture: every storage field gets `ceil(width/8)` parity bits sliced from its LSB; a continuous combinational comparator feeds a sticky per-field error vector cleared by a shared `error_clear_i` input; transient single-bit injection is driven by a flat-indexed SV port (`parity_inject_sel` + `parity_inject_strobe`); per-field and per-parity-bit `localparam` enumerations are emitted in the generated package so external self-test logic can address bits by name. External addressable components are skipped (matching today's behavior). Source spec: `docs/superpowers/specs/2026-04-28-bytewise-parity-design.md`.

**Tech Stack:** Python 3 (PeakRDL exporter), Jinja2 (SV templates), SystemRDL/peakrdl-regblock conventions, SystemVerilog (generated output), pytest (test harness).

---

## Pre-flight: pytest must work

Before starting Task 1, confirm pytest is available and the existing suite collects:

```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -m pytest tests/test_parity --collect-only -q
```

Expected: collection lists `Test::test_dut`. If the command fails (pytest not installed, environment not sourced, simulator dependency missing on collection), **STOP and ask the user how to run tests in this environment.** The user's standard project setup typically requires sourcing an env script (e.g. `source bin/setup_env.sh`) — they will tell you which one. Do not improvise or proceed without test execution working.

The same rule applies for Task 11 (behavioral simulation) — that step needs both pytest and a configured Verilog simulator; if either is missing, STOP and ask.

---

## File Structure

### Modified files

| Path | Responsibility |
|---|---|
| `src/peakrdl_regblock/__peakrdl__.py` | CLI plugin — add `--odd-parity` and `--parity-byte` arguments; thread to `do_export`. |
| `src/peakrdl_regblock/exporter.py` | `RegblockExporter.export()` accepts `odd_parity` and `bytewise_parity` kwargs; `DesignState` stores them and the parity enumeration tables; `get_module_port_list()` emits new top-level ports when bytewise mode is enabled. |
| `src/peakrdl_regblock/scan_design.py` | When `bytewise_parity` is set, walk the design and populate `ds.parity_fields` (the flat per-field enumeration) and `ds.parity_bits` (the flat per-parity-bit enumeration). Skip externals. Suppress the legacy paritycheck "missing reset" warning when bytewise is on. |
| `src/peakrdl_regblock/parity.py` | Keep `ParityErrorReduceGenerator` (legacy). Add `BytewiseParityPackageGenerator`, `BytewiseParityModuleGenerator` for SV emission, plus a small `parity_path_id(field, byte=None)` helper that produces SV-legal localparam names. |
| `src/peakrdl_regblock/field_logic/generators.py` | `FieldStorageStructGenerator` adds a `parity[B]` array for parity-protected fields when bytewise mode is on (`B = ceil(W/8)`). `CombinationalStructGenerator` adds `mismatch[B]` and `inject_hit[B]` arrays. |
| `src/peakrdl_regblock/field_logic/templates/field_storage.sv` | New Jinja branches for per-byte parity load (gated on `ds.has_bytewise_parity`), per-byte mismatch combo with optional `inject_hit` XOR, and per-byte parity reset. Polarity controlled by `ds.odd_parity`. Legacy `paritycheck` branches retain their behavior modulo `ds.odd_parity`. |
| `src/peakrdl_regblock/module_tmpl.sv` | When `ds.has_bytewise_parity`, emit the sticky-error always_ff, the inject one-hot decoder, the per-field mismatch reducers, and the `field_parity_error` driver. |
| `src/peakrdl_regblock/package_tmpl.sv` | Emit `N_PARITY_FIELDS`, `N_PARITY_BITS`, `FERR_IDX_*`, `PINJ_IDX_*`, `PINJ_TO_FERR[]` localparams + comment table when bytewise mode is on. |
| `src/peakrdl_regblock/field_logic/__init__.py` | Add `get_parity_byte_storage_identifier(field, byte)` and `get_parity_byte_mismatch_identifier(field, byte)` helpers. |
| `tests/test_parity/testcase.py` | Add a second test class running the same legacy RDL with `odd_parity=True` to validate the inverter path. |
| `tests/test_parity/tb_template.sv` | No change needed for the legacy-parity test; the comparison is `parity != [~]^value` either way. |
| `tests/lib/base_testcase.py` | Add `odd_parity` and `bytewise_parity` class attributes (default False); pass through to `RegblockExporter.export()`. |

### New files

| Path | Responsibility |
|---|---|
| `tests/test_parity_bytewise/__init__.py` | Empty marker. |
| `tests/test_parity_bytewise/regblock.rdl` | New RDL exercising: multi-byte field with non-byte-aligned width, `sw=rw,hw=r` field, `sw=r,hw=w` field with no enable, `sw=r,hw=w` field with `we`, compound interrupt field, counter, and an external register that should be skipped. |
| `tests/test_parity_bytewise/testcase.py` | One test class with `bytewise_parity=True`, plus a second with `bytewise_parity=True, odd_parity=True`. |
| `tests/test_parity_bytewise/tb_template.sv` | Behavioral test sequence covering all numbered cases from spec section 9 (SEU detect, sticky, clear, injection, partial-write, reset). |
| `CHANGE.md` | Top-level user-facing changelog. Concise, bullet-list. |

---

## Task 1: Add `--odd-parity` CLI flag and DesignState plumbing

**Files:**
- Modify: `src/peakrdl_regblock/exporter.py`
- Modify: `src/peakrdl_regblock/__peakrdl__.py`
- Modify: `tests/lib/base_testcase.py`

- [ ] **Step 1.1: Add `odd_parity` to `DesignState`**

Edit `src/peakrdl_regblock/exporter.py`. After line 280 (`self.err_if_bad_rw = ...`), add:

```python
        # Parity polarity
        self.odd_parity = kwargs.pop("odd_parity", False) # type: bool
```

- [ ] **Step 1.2: Add CLI flag**

Edit `src/peakrdl_regblock/__peakrdl__.py`. After the existing `--err-if-bad-rw` block (ending at line 164, the closing `)` of `add_argument("--err-if-bad-rw", ...)`), add:

```python
        arg_group.add_argument(
            "--odd-parity",
            action="store_true",
            default=False,
            help="""When parity logic is generated, use odd parity (parity bit
            inverted) instead of the default even parity. Applies to fields with
            the 'paritycheck' RDL property and to byte-wise parity (--parity-byte)."""
        )
```

Then in `do_export()` at the existing `x.export(...)` call (line 211), add a new kwarg:

```python
            odd_parity=options.odd_parity,
```

(Place it after `default_reset_async=default_reset_async,` on line 229.)

- [ ] **Step 1.3: Pass `odd_parity` through `base_testcase`**

Edit `tests/lib/base_testcase.py`. After line 43 (`err_if_bad_rw = False`), add:

```python
    odd_parity = False
```

In `export_regblock()` at the `self.exporter.export(...)` call (lines 108-125), add a new kwarg before the closing `)`:

```python
            odd_parity=self.odd_parity,
```

- [ ] **Step 1.4: Run existing tests to confirm no regression**

Run:
```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -m pytest tests/test_parity -k "test_dut" --collect-only
```

Expected: collection succeeds, shows `test_dut` test. No errors.

**If pytest is not available or the suite refuses to collect, STOP and ask the user.** Do not skip the test run; do not improvise with `python -c`. The user has explicitly required pytest as the test runner of record. The user can tell you how to source the environment, install pytest, or otherwise enable the test suite. Resume from here once they've confirmed.

- [ ] **Step 1.5: Commit**

```bash
git add src/peakrdl_regblock/exporter.py src/peakrdl_regblock/__peakrdl__.py tests/lib/base_testcase.py
git commit -m "Add --odd-parity flag plumbing"
```

---

## Task 2: Wire `odd_parity` into the legacy field_storage template

**Files:**
- Modify: `src/peakrdl_regblock/field_logic/templates/field_storage.sv`

- [ ] **Step 2.1: Read the current template**

Open `src/peakrdl_regblock/field_logic/templates/field_storage.sv`. Note the three current parity references at lines 43-45, 54-56, 63-65, and 78-80. They all use `^` (even parity).

- [ ] **Step 2.2: Replace `^` with polarity-aware expression in all three sites**

Edit `src/peakrdl_regblock/field_logic/templates/field_storage.sv`.

Site A — line 43-45 (combinational comparator):

Replace:
```
    {%- if node.get_property('paritycheck') %}
    {{field_logic.get_parity_error_identifier(node)}} = ({{field_logic.get_parity_identifier(node)}} != ^{{field_logic.get_storage_identifier(node)}});
    {%- endif %}
```

With:
```
    {%- if node.get_property('paritycheck') %}
    {{field_logic.get_parity_error_identifier(node)}} = ({{field_logic.get_parity_identifier(node)}} != {% if ds.odd_parity %}~{% endif %}^{{field_logic.get_storage_identifier(node)}});
    {%- endif %}
```

Site B — line 54-56 (reset value):

Replace:
```
        {%- if node.get_property('paritycheck') %}
        {{field_logic.get_parity_identifier(node)}} <= ^{{reset}};
        {%- endif %}
```

With:
```
        {%- if node.get_property('paritycheck') %}
        {{field_logic.get_parity_identifier(node)}} <= {% if ds.odd_parity %}~{% endif %}^{{reset}};
        {%- endif %}
```

Site C — line 63-65 (load_next with reset variant):

Replace:
```
            {%- if node.get_property('paritycheck') %}
            {{field_logic.get_parity_identifier(node)}} <= ^{{field_logic.get_field_combo_identifier(node, "next")}};
            {%- endif %}
```

With:
```
            {%- if node.get_property('paritycheck') %}
            {{field_logic.get_parity_identifier(node)}} <= {% if ds.odd_parity %}~{% endif %}^{{field_logic.get_field_combo_identifier(node, "next")}};
            {%- endif %}
```

Site D — line 78-80 (load_next without reset):

Replace:
```
        {%- if node.get_property('paritycheck') %}
        {{field_logic.get_parity_identifier(node)}} <= ^{{field_logic.get_field_combo_identifier(node, "next")}};
        {%- endif %}
```

With:
```
        {%- if node.get_property('paritycheck') %}
        {{field_logic.get_parity_identifier(node)}} <= {% if ds.odd_parity %}~{% endif %}^{{field_logic.get_field_combo_identifier(node, "next")}};
        {%- endif %}
```

- [ ] **Step 2.3: Add `odd_parity` test variant to `test_parity`**

Edit `tests/test_parity/testcase.py`. Replace its contents with:

```python
from ..lib.sim_testcase import SimTestCase

class Test(SimTestCase):
    def test_dut(self):
        self.run_test()

class TestOddParity(SimTestCase):
    odd_parity = True

    def test_dut(self):
        self.run_test()
```

- [ ] **Step 2.4: Verify export still works (sanity)**

```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -c "
import os, glob
from systemrdl import RDLCompiler
from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.udps import ALL_UDPS

rdlc = RDLCompiler()
for udp in ALL_UDPS:
    rdlc.register_udp(udp)
rdlc.compile_file('hdl-src/regblock_udps.rdl')
rdlc.compile_file('tests/test_parity/regblock.rdl')
root = rdlc.elaborate()
out = '/tmp/regblock_odd_test'
os.makedirs(out, exist_ok=True)
RegblockExporter().export(root, out, module_name='regblock', package_name='regblock_pkg', odd_parity=True)
with open(os.path.join(out, 'regblock.sv')) as f:
    sv = f.read()
assert '~^' in sv, 'odd parity inverter not found in output'
print('OK')
"
```

Expected: prints `OK`. The generated SV contains `~^` somewhere (the inverter on parity computations).

- [ ] **Step 2.5: Commit**

```bash
git add src/peakrdl_regblock/field_logic/templates/field_storage.sv tests/test_parity/testcase.py
git commit -m "Wire --odd-parity through legacy paritycheck template"
```

---

## Task 3: Add `bytewise_parity` flag and `DesignState` parity collections

**Files:**
- Modify: `src/peakrdl_regblock/exporter.py`
- Modify: `src/peakrdl_regblock/__peakrdl__.py`
- Modify: `tests/lib/base_testcase.py`

- [ ] **Step 3.1: Add `bytewise_parity` plus the parity collections to `DesignState`**

Edit `src/peakrdl_regblock/exporter.py`. After the `self.odd_parity = ...` line added in Task 1 (Step 1.1), add:

```python
        self.bytewise_parity = kwargs.pop("bytewise_parity", False) # type: bool
```

Then locate the existing line `self.has_paritycheck = False` (was line 298 before edits). Right after it, add:

```python
        # Bytewise parity bookkeeping. Populated by DesignScanner when
        # bytewise_parity is True. Each entry is a tuple:
        #   parity_fields: (field_node, byte_count, ferr_idx, first_pinj_idx)
        #   parity_bits:   (field_node, byte_index, slice_lo, slice_hi, pinj_idx, ferr_idx)
        self.has_bytewise_parity = False # type: bool
        self.parity_fields = [] # type: List[tuple]
        self.parity_bits = [] # type: List[tuple]
```

Update the imports at the top of the file to include `List` from typing and `Tuple` (it already imports `List` — confirm by reading line 2).

- [ ] **Step 3.2: Add CLI flag**

Edit `src/peakrdl_regblock/__peakrdl__.py`. After the `--odd-parity` block from Task 1 Step 1.2, add:

```python
        arg_group.add_argument(
            "--parity-byte",
            action="store_true",
            default=False,
            help="""Enable byte-wise per-field parity protection across the
            entire design. Adds a sticky per-field parity_error vector,
            single-bit injection port, and a shared error_clear_i input.
            When set, the per-field paritycheck RDL property is ignored —
            every storage field is protected."""
        )
```

In `do_export()`, at the `x.export(...)` call, add the kwarg next to `odd_parity`:

```python
            bytewise_parity=options.parity_byte,
```

(Note: argparse converts `--parity-byte` to `parity_byte` for the attribute.)

- [ ] **Step 3.3: Pass `bytewise_parity` through `base_testcase.py`**

Edit `tests/lib/base_testcase.py`. After the `odd_parity = False` line from Task 1 Step 1.3, add:

```python
    bytewise_parity = False
```

In `export_regblock()`, add the kwarg next to `odd_parity`:

```python
            bytewise_parity=self.bytewise_parity,
```

- [ ] **Step 3.4: Verify by exporting with the flag and inspecting `ds`**

Run:
```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -c "
import os
from systemrdl import RDLCompiler
from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.udps import ALL_UDPS

rdlc = RDLCompiler()
for udp in ALL_UDPS:
    rdlc.register_udp(udp)
rdlc.compile_file('hdl-src/regblock_udps.rdl')
rdlc.compile_file('tests/test_parity/regblock.rdl')
root = rdlc.elaborate()
out = '/tmp/regblock_bw_test'
os.makedirs(out, exist_ok=True)
e = RegblockExporter()
e.export(root, out, module_name='regblock', package_name='regblock_pkg', bytewise_parity=True)
print('bytewise_parity:', e.ds.bytewise_parity)
print('has_bytewise_parity:', e.ds.has_bytewise_parity)
print('parity_fields:', e.ds.parity_fields)
print('OK')
"
```

Expected: prints `bytewise_parity: True`, `has_bytewise_parity: False` (we haven't populated it yet — that's Task 4), `parity_fields: []`, then `OK`.

- [ ] **Step 3.5: Commit**

```bash
git add src/peakrdl_regblock/exporter.py src/peakrdl_regblock/__peakrdl__.py tests/lib/base_testcase.py
git commit -m "Add --parity-byte flag plumbing"
```

---

## Task 4: Populate `parity_fields` and `parity_bits` in `DesignScanner`

**Files:**
- Modify: `src/peakrdl_regblock/scan_design.py`

The bytewise enumeration must include each array-instance separately (e.g. `r2[8]` produces 8 entries per parity-protected field, not 1). The existing `RDLWalker()` runs with `unroll=False`, which visits array templates once. For the parity pass we need a second walk with `unroll=True`.

- [ ] **Step 4.1: Adjust legacy `paritycheck` handling when bytewise mode is on**

Edit `src/peakrdl_regblock/scan_design.py`. Replace the current `enter_Field` (lines 104-121) with:

```python
    def enter_Field(self, node: 'FieldNode') -> None:
        if node.is_sw_writable and (node.msb < node.lsb):
            self.ds.has_writable_msb0_fields = True

        if node.get_property('paritycheck') and node.implements_storage:
            if self.ds.bytewise_parity:
                # Bytewise mode covers every storage field; the per-field
                # paritycheck property is redundant. Warn the user so they
                # notice and can clean up the RDL.
                self.msg.warning(
                    f"Field '{node.inst_name}' has 'paritycheck' set, but the "
                    "regblock is being generated with --parity-byte. The new "
                    "byte-wise parity architecture covers every storage field; "
                    "the per-field paritycheck property is ignored in this mode "
                    "and can be removed from the RDL.",
                    self.top_node.property_src_ref.get('paritycheck', self.top_node.inst_src_ref)
                )
            else:
                # Legacy mode: only fields explicitly tagged.
                self.ds.has_paritycheck = True

                if node.get_property('reset') is None:
                    self.msg.warning(
                        f"Field '{node.inst_name}' includes parity check logic, but "
                        "its reset value was not defined. Will result in an undefined "
                        "value on the module's 'parity_error' output.",
                        self.top_node.property_src_ref.get('paritycheck', self.top_node.inst_src_ref)
                    )

        encode = node.get_property("encode")
        if encode and encode not in self.ds.user_enums:
            self.ds.user_enums.append(encode)
```

- [ ] **Step 4.2: Add the bytewise scanner listener and a second walker pass**

Edit the same file. After the existing `DesignScanner` class, append:

```python
class _BytewiseParityScanner(RDLListener):
    """Second-pass listener (unroll=True) that populates the bytewise
    parity enumerations on the design state."""

    def __init__(self, ds: 'DesignState') -> None:
        self.ds = ds

    def enter_Component(self, node: 'Node') -> Optional[WalkerAction]:
        # Skip externals — same rule as the main scanner.
        if node.external and node != self.ds.top_node:
            return WalkerAction.SkipDescendants
        return WalkerAction.Continue

    def enter_Field(self, node: 'FieldNode') -> None:
        if not node.implements_storage:
            return

        self.ds.has_bytewise_parity = True

        width = node.width
        byte_count = (width + 7) // 8

        ferr_idx = len(self.ds.parity_fields)
        first_pinj_idx = len(self.ds.parity_bits)

        self.ds.parity_fields.append((node, byte_count, ferr_idx, first_pinj_idx))

        for i in range(byte_count):
            slice_lo = 8 * i
            slice_hi = min(8 * i + 7, width - 1)
            pinj_idx = first_pinj_idx + i
            self.ds.parity_bits.append(
                (node, i, slice_lo, slice_hi, pinj_idx, ferr_idx)
            )
```

Then in `DesignScanner.do_scan()` (around line 60), after the existing `RDLWalker().walk(self.top_node, self)` line, add:

```python
        # Bytewise parity needs unrolled array instances.
        if self.ds.bytewise_parity:
            RDLWalker(unroll=True).walk(self.top_node, _BytewiseParityScanner(self.ds))
```

- [ ] **Step 4.3: Add a Python unit test asserting enumeration correctness**

Create `tests/unit/test_parity_scan.py`:

```python
"""Unit tests for the bytewise-parity scanner population in DesignState."""
import os
from systemrdl import RDLCompiler
from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.udps import ALL_UDPS


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _elaborate(rdl_relpath: str):
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
    rdlc = RDLCompiler()
    for udp in ALL_UDPS:
        rdlc.register_udp(udp)
    rdlc.compile_file(os.path.join(REPO_ROOT, "hdl-src/regblock_udps.rdl"))
    # tests/test_parity/regblock.rdl has `default paritycheck;` so every field is tagged.
    rdlc.compile_file(os.path.join(REPO_ROOT, "tests/test_parity/regblock.rdl"))
    root = rdlc.elaborate()
    initial_warnings = root.env.msg.warning_count

    e = RegblockExporter()
    e.export(
        root, str(tmp_path),
        module_name="regblock", package_name="regblock_pkg",
        bytewise_parity=True,
    )
    final_warnings = root.env.msg.warning_count
    assert final_warnings > initial_warnings, (
        "Expected at least one warning when paritycheck and --parity-byte are both on; "
        f"warning_count went {initial_warnings} -> {final_warnings}"
    )


def test_paritycheck_alone_no_redundancy_warning(tmp_path):
    """Sanity: legacy mode with paritycheck and reset values defined should not
    emit the new redundancy warning."""
    rdlc = RDLCompiler()
    for udp in ALL_UDPS:
        rdlc.register_udp(udp)
    rdlc.compile_file(os.path.join(REPO_ROOT, "hdl-src/regblock_udps.rdl"))
    rdlc.compile_file(os.path.join(REPO_ROOT, "tests/test_parity/regblock.rdl"))
    root = rdlc.elaborate()
    initial_warnings = root.env.msg.warning_count

    e = RegblockExporter()
    e.export(
        root, str(tmp_path),
        module_name="regblock", package_name="regblock_pkg",
        # bytewise_parity defaults to False
    )
    # All fields in the test RDL have explicit reset values, so the legacy
    # "missing reset" warning should not fire either.
    assert root.env.msg.warning_count == initial_warnings, (
        f"Unexpected warnings in legacy mode: "
        f"{initial_warnings} -> {root.env.msg.warning_count}"
    )
```

Create directory if needed:
```bash
mkdir -p tests/unit
touch tests/unit/__init__.py
```

- [ ] **Step 4.4: Run the unit tests**

```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -m pytest tests/unit/test_parity_scan.py -v
```

Expected: 5 tests pass (the three field-enumeration tests, the redundancy-warning test, and the legacy-mode no-warning sanity test). **If pytest is not available or the suite cannot run, STOP and ask the user how to run tests in this environment — do not silently fall back to a Python sanity check.**

- [ ] **Step 4.5: Commit**

```bash
git add src/peakrdl_regblock/scan_design.py tests/unit/test_parity_scan.py tests/unit/__init__.py
git commit -m "Populate parity enumeration tables in DesignScanner"
```

---

## Task 5: Add `parity_path_id` helper and field_logic identifier helpers

**Files:**
- Modify: `src/peakrdl_regblock/parity.py`
- Modify: `src/peakrdl_regblock/field_logic/__init__.py`

- [ ] **Step 5.1: Add `parity_path_id` helper to `parity.py`**

Edit `src/peakrdl_regblock/parity.py`. After the existing imports and class, append:

```python


def parity_path_id(top_node: 'AddrmapNode', field: 'FieldNode', byte: int = None) -> str:
    """Build an SV-legal identifier suffix from a field path, e.g.:

        r1.f1            -> 'R1_F1'
        r2[3].f1         -> 'R2_3_F1'
        r2[i0].f1, byte=2 -> 'R2_I0_F1_BYTE2'

    Used to construct FERR_IDX_<id> and PINJ_IDX_<id>_BYTE<i> localparam names.
    """
    from .utils import get_indexed_path
    path = get_indexed_path(top_node, field)
    # Replace `.`, `[`, `]` with `_`. Strip trailing `_`.
    sv_id = path.replace('.', '_').replace('[', '_').replace(']', '').upper()
    sv_id = sv_id.rstrip('_')
    if byte is not None:
        sv_id = f"{sv_id}_BYTE{byte}"
    return sv_id
```

- [ ] **Step 5.2: Add field-logic identifier helpers**

Edit `src/peakrdl_regblock/field_logic/__init__.py`. After the existing `get_parity_error_identifier` method (around line 283), add:

```python
    def get_parity_byte_storage_identifier(self, field: 'FieldNode', byte: int) -> str:
        """
        Returns the Verilog string referencing one byte of the bytewise-parity
        storage for `field`, e.g. `field_storage.r1.f1.parity[0]`.
        """
        assert field.implements_storage
        path = get_indexed_path(self.top_node, field)
        return f"field_storage.{path}.parity[{byte}]"

    def get_parity_byte_mismatch_identifier(self, field: 'FieldNode', byte: int) -> str:
        """
        Returns the Verilog string referencing one byte of the bytewise-parity
        mismatch combo signal, e.g. `field_combo.r1.f1.mismatch[0]`.
        """
        assert field.implements_storage
        path = get_indexed_path(self.top_node, field)
        return f"field_combo.{path}.mismatch[{byte}]"

    def get_parity_byte_inject_hit_identifier(self, field: 'FieldNode', byte: int) -> str:
        """
        Returns the Verilog string referencing one byte of the bytewise-parity
        injection-hit combo signal, e.g. `field_combo.r1.f1.inject_hit[0]`.
        """
        assert field.implements_storage
        path = get_indexed_path(self.top_node, field)
        return f"field_combo.{path}.inject_hit[{byte}]"
```

`get_indexed_path` is already imported at the top of the file (line 14).

- [ ] **Step 5.3: Add unit tests for `parity_path_id`**

Append to `tests/unit/test_parity_scan.py`:

```python


def test_parity_path_id_format(tmp_path):
    from peakrdl_regblock.parity import parity_path_id

    root = _elaborate("tests/test_parity/regblock.rdl")
    e = RegblockExporter()
    e.export(
        root, str(tmp_path),
        module_name="regblock", package_name="regblock_pkg",
        bytewise_parity=True,
    )

    # The first parity field should be r1.f1 (depth-first ordering).
    first_node, *_ = e.ds.parity_fields[0]
    assert parity_path_id(e.ds.top_node, first_node) == "R1_F1"
    assert parity_path_id(e.ds.top_node, first_node, byte=0) == "R1_F1_BYTE0"
    assert parity_path_id(e.ds.top_node, first_node, byte=1) == "R1_F1_BYTE1"
```

- [ ] **Step 5.4: Run the unit tests**

```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -m pytest tests/unit/test_parity_scan.py -v
```

Expected: all 4 tests pass. **If pytest is not available, STOP and ask the user.**

- [ ] **Step 5.5: Commit**

```bash
git add src/peakrdl_regblock/parity.py src/peakrdl_regblock/field_logic/__init__.py tests/unit/test_parity_scan.py
git commit -m "Add bytewise-parity path/identifier helpers"
```

---

## Task 6: Extend storage and combo struct generators with parity arrays

**Files:**
- Modify: `src/peakrdl_regblock/field_logic/generators.py`

- [ ] **Step 6.1: Extend `FieldStorageStructGenerator`**

Edit `src/peakrdl_regblock/field_logic/generators.py`. Locate the `enter_Field` method on `FieldStorageStructGenerator` (lines 89-100). Replace with:

```python
    def enter_Field(self, node: 'FieldNode') -> None:
        self.push_struct(kwf(node.inst_name))

        if node.implements_storage:
            self.add_member("value", node.width)
            if self.field_logic.ds.bytewise_parity:
                byte_count = (node.width + 7) // 8
                self.add_member("parity", byte_count)
            elif node.get_property('paritycheck'):
                self.add_member("parity")

        if self.field_logic.has_next_q(node):
            self.add_member("next_q", node.width)

        self.pop_struct()
```

- [ ] **Step 6.2: Extend `CombinationalStructGenerator`**

Edit the same file. Locate `enter_Field` on `CombinationalStructGenerator` (around lines 32-59). Replace the trailing parity branch (current lines 57-58):

```python
        if node.get_property('paritycheck'):
            self.add_member("parity_error")
        self.pop_struct()
```

With:

```python
        if self.field_logic.ds.bytewise_parity and node.implements_storage:
            byte_count = (node.width + 7) // 8
            self.add_member("mismatch", byte_count)
            self.add_member("inject_hit", byte_count)
        elif node.get_property('paritycheck'):
            self.add_member("parity_error")
        self.pop_struct()
```

- [ ] **Step 6.3: Verify struct emission**

```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -c "
import os
from systemrdl import RDLCompiler
from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.udps import ALL_UDPS

rdlc = RDLCompiler()
for udp in ALL_UDPS:
    rdlc.register_udp(udp)
rdlc.compile_file('hdl-src/regblock_udps.rdl')
rdlc.compile_file('tests/test_parity/regblock.rdl')
root = rdlc.elaborate()
out = '/tmp/regblock_bw_struct'
os.makedirs(out, exist_ok=True)
RegblockExporter().export(root, out, module_name='regblock', package_name='regblock_pkg', bytewise_parity=True)
sv = open(os.path.join(out, 'regblock.sv')).read()
# f1 is 16-bit -> 2 parity bytes, 2 mismatch, 2 inject_hit.
assert 'logic [1:0] parity' in sv, 'expected per-field parity[2] member for 16-bit field'
assert 'mismatch' in sv, 'expected mismatch combo member'
assert 'inject_hit' in sv, 'expected inject_hit combo member'
print('OK')
"
```

Expected: prints `OK`. (Note: at this point the SV will *not* compile cleanly because we haven't driven the new combo signals yet — that's Task 7. The struct emission is what we're verifying here.)

- [ ] **Step 6.4: Commit**

```bash
git add src/peakrdl_regblock/field_logic/generators.py
git commit -m "Emit per-byte parity/mismatch/inject_hit struct members"
```

---

## Task 7: Extend `field_storage.sv` template with byte-wise parity logic

**Files:**
- Modify: `src/peakrdl_regblock/field_logic/templates/field_storage.sv`

- [ ] **Step 7.1: Add the bytewise-parity combinational comparator block**

Edit `src/peakrdl_regblock/field_logic/templates/field_storage.sv`. After the existing combinational `paritycheck` block (which now ends at the line containing `^{{...storage}});` after Task 2's edit, around line 45), but BEFORE the closing `end` of the `always_comb` (line 46), insert:

```
    {%- if ds.bytewise_parity and node.implements_storage %}
    {%- set byte_count = ((node.width + 7) // 8) %}
    {%- for i in range(byte_count) %}
    {%- set slice_lo = 8 * i %}
    {%- set slice_hi = ([8 * i + 7, node.width - 1] | min) %}
    {%- set w = slice_hi - slice_lo + 1 %}
    {{field_logic.get_parity_byte_mismatch_identifier(node, i)}} = ({{field_logic.get_parity_byte_storage_identifier(node, i)}} != ({% if ds.odd_parity %}~{% endif %}^{{field_logic.get_storage_identifier(node)}}[{{slice_hi}}:{{slice_lo}}] ^ {{field_logic.get_parity_byte_inject_hit_identifier(node, i)}}));
    {%- endfor %}
    {%- endif %}
```

- [ ] **Step 7.2: Add bytewise-parity reset and load_next branches**

Still in `field_storage.sv`. There are two `always_ff` blocks: one with reset (lines 50-71 originally) and one without reset (lines 75-86 originally).

In the **with-reset** block, after the existing legacy paritycheck branch inside the `if(reset)` clause (around line 56), insert:

```
        {%- if ds.bytewise_parity and node.implements_storage and reset is not none %}
        {%- set byte_count = ((node.width + 7) // 8) %}
        {%- for i in range(byte_count) %}
        {%- set slice_lo = 8 * i %}
        {%- set slice_hi = ([8 * i + 7, node.width - 1] | min) %}
        {{field_logic.get_parity_byte_storage_identifier(node, i)}} <= {% if ds.odd_parity %}~{% endif %}^(({{node.width}}'({{reset}})) >> {{slice_lo}});
        {%- endfor %}
        {%- endif %}
```

The `(width'(reset)) >> slice_lo` form casts the reset value to the field width then right-shifts to bring the desired byte to the bottom. The XOR-reduce ignores the now-zeroed high bits, which is the correct parity of the slice. This avoids relying on part-select syntax on arbitrary expressions, which some older SV tools reject.

Then in the same with-reset block, inside `if(load_next)` (after the existing legacy paritycheck assignment around line 64), insert:

```
            {%- if ds.bytewise_parity and node.implements_storage %}
            {%- set byte_count = ((node.width + 7) // 8) %}
            {%- for i in range(byte_count) %}
            {%- set slice_lo = 8 * i %}
            {%- set slice_hi = ([8 * i + 7, node.width - 1] | min) %}
            {{field_logic.get_parity_byte_storage_identifier(node, i)}} <= {% if ds.odd_parity %}~{% endif %}^{{field_logic.get_field_combo_identifier(node, "next")}}[{{slice_hi}}:{{slice_lo}}];
            {%- endfor %}
            {%- endif %}
```

In the **without-reset** block (the `else` branch, around line 76), inside `if(load_next)` (after the existing legacy paritycheck assignment), insert the same load_next-bytewise block:

```
        {%- if ds.bytewise_parity and node.implements_storage %}
        {%- set byte_count = ((node.width + 7) // 8) %}
        {%- for i in range(byte_count) %}
        {%- set slice_lo = 8 * i %}
        {%- set slice_hi = ([8 * i + 7, node.width - 1] | min) %}
        {{field_logic.get_parity_byte_storage_identifier(node, i)}} <= {% if ds.odd_parity %}~{% endif %}^{{field_logic.get_field_combo_identifier(node, "next")}}[{{slice_hi}}:{{slice_lo}}];
        {%- endfor %}
        {%- endif %}
```

- [ ] **Step 7.3: Verify SV emission contains the new parity logic**

```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -c "
import os
from systemrdl import RDLCompiler
from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.udps import ALL_UDPS

rdlc = RDLCompiler()
for udp in ALL_UDPS:
    rdlc.register_udp(udp)
rdlc.compile_file('hdl-src/regblock_udps.rdl')
rdlc.compile_file('tests/test_parity/regblock.rdl')
root = rdlc.elaborate()
out = '/tmp/regblock_bw_template'
os.makedirs(out, exist_ok=True)
RegblockExporter().export(root, out, module_name='regblock', package_name='regblock_pkg', bytewise_parity=True)
sv = open(os.path.join(out, 'regblock.sv')).read()
# Should reference the per-byte mismatch and parity[]
assert '.mismatch[0]' in sv, 'expected mismatch[0] reference'
assert '.parity[0]' in sv, 'expected parity[0] storage'
assert 'inject_hit' in sv, 'expected inject_hit reference'
print('OK')
"
```

Expected: prints `OK`.

- [ ] **Step 7.4: Commit**

```bash
git add src/peakrdl_regblock/field_logic/templates/field_storage.sv
git commit -m "Emit per-byte parity load and mismatch in field_storage template"
```

---

## Task 8: Add `BytewiseParityModuleGenerator` in `parity.py`

**Files:**
- Modify: `src/peakrdl_regblock/parity.py`

- [ ] **Step 8.1: Add the module-side generator class**

Edit `src/peakrdl_regblock/parity.py`. After the existing `ParityErrorReduceGenerator` class and the `parity_path_id` helper from Task 5, append:

```python


class BytewiseParityModuleGenerator:
    """
    Emits the SV that lives in module_tmpl.sv when --parity-byte is on:
      - per-field error reducer (OR of mismatch bytes)
      - per-parity-bit one-hot inject decoder
      - sticky field_parity_error always_ff
    """

    def __init__(self, exp: 'RegblockExporter') -> None:
        self.exp = exp

    @property
    def ds(self) -> 'DesignState':
        return self.exp.ds

    def get_inject_decode(self) -> str:
        """Combinational decoder: drives field_combo.<path>.inject_hit[i] for each parity bit."""
        if not self.ds.has_bytewise_parity:
            return ""
        from .field_logic import FieldLogic  # local import to avoid cycles
        fl = self.exp.field_logic
        lines = []
        for (node, byte, _lo, _hi, pinj_idx, _ferr_idx) in self.ds.parity_bits:
            ident = fl.get_parity_byte_inject_hit_identifier(node, byte)
            lines.append(
                f"assign {ident} = parity_inject_strobe & "
                f"(parity_inject_sel == {pinj_idx});"
            )
        return "\n".join(lines)

    def get_field_error_reducers(self) -> str:
        """For each parity field, OR all its mismatch bytes into a single combinational signal."""
        if not self.ds.has_bytewise_parity:
            return ""
        fl = self.exp.field_logic
        lines = []
        for (node, byte_count, ferr_idx, _first_pinj) in self.ds.parity_fields:
            ident = parity_path_id(self.ds.top_node, node)
            mismatch_terms = " | ".join(
                fl.get_parity_byte_mismatch_identifier(node, b)
                for b in range(byte_count)
            )
            lines.append(f"logic field_parity_mismatch_{ident};")
            lines.append(f"assign field_parity_mismatch_{ident} = {mismatch_terms};")
        return "\n".join(lines)

    def get_sticky_latch_block(self) -> str:
        """Always_ff that latches each per-field mismatch into the sticky field_parity_error vector."""
        if not self.ds.has_bytewise_parity:
            return ""
        lines = []
        for (node, _bc, ferr_idx, _fp) in self.ds.parity_fields:
            ident = parity_path_id(self.ds.top_node, node)
            lines.append(
                f"if (error_clear_i) field_parity_error[{ferr_idx}] <= 1'b0;"
            )
            lines.append(
                f"else if (field_parity_mismatch_{ident}) "
                f"field_parity_error[{ferr_idx}] <= 1'b1;"
            )
        return "\n".join(lines)
```

- [ ] **Step 8.2: Wire it into the exporter context**

Edit `src/peakrdl_regblock/exporter.py`. At the imports near line 22, add to the existing parity import:

```python
from .parity import ParityErrorReduceGenerator, BytewiseParityModuleGenerator
```

In the `export()` method, near where `parity = ParityErrorReduceGenerator(self)` is created (around line 163), add:

```python
        bytewise_parity_mod = BytewiseParityModuleGenerator(self)
```

And in the context dict (around line 184), add:

```python
            "bytewise_parity_mod": bytewise_parity_mod,
```

- [ ] **Step 8.3: Sanity-check no import cycles or attribute errors**

```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -c "
import os
from systemrdl import RDLCompiler
from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.udps import ALL_UDPS

rdlc = RDLCompiler()
for udp in ALL_UDPS:
    rdlc.register_udp(udp)
rdlc.compile_file('hdl-src/regblock_udps.rdl')
rdlc.compile_file('tests/test_parity/regblock.rdl')
root = rdlc.elaborate()
out = '/tmp/regblock_bw_mod'
os.makedirs(out, exist_ok=True)
RegblockExporter().export(root, out, module_name='regblock', package_name='regblock_pkg', bytewise_parity=True)
print('OK')
"
```

Expected: prints `OK`. (Generated SV will still be incomplete — Task 9 wires the new generator into the templates.)

- [ ] **Step 8.4: Commit**

```bash
git add src/peakrdl_regblock/parity.py src/peakrdl_regblock/exporter.py
git commit -m "Add BytewiseParityModuleGenerator and helpers"
```

---

## Task 9: Emit top-level ports + sticky latch block in `module_tmpl.sv`

**Files:**
- Modify: `src/peakrdl_regblock/exporter.py` (port list)
- Modify: `src/peakrdl_regblock/module_tmpl.sv`

- [ ] **Step 9.1: Add bytewise-parity ports to `get_module_port_list`**

Edit `src/peakrdl_regblock/exporter.py`. In `get_module_port_list()` (lines 212-243), after the existing `if self.ds.has_paritycheck` block (lines 233-235), add:

```python
        # Bytewise parity ports
        if self.ds.has_bytewise_parity:
            n_fields = len(self.ds.parity_fields)
            n_bits = len(self.ds.parity_bits)
            sel_w = max(1, (n_bits - 1).bit_length())
            bw_ports = [
                f"output logic [{n_fields - 1}:0] field_parity_error",
                "input  logic                            error_clear_i",
                f"input  logic [{sel_w - 1}:0] parity_inject_sel",
                "input  logic                            parity_inject_strobe",
            ]
            groups.append(",\n".join(bw_ports))
```

- [ ] **Step 9.2: Emit the sticky latch + reducers in `module_tmpl.sv`**

Edit `src/peakrdl_regblock/module_tmpl.sv`. After the existing legacy `Parity Error` block (which ends at the `endif` on line 201), add:

```
{%- if ds.has_bytewise_parity %}

    //--------------------------------------------------------------------------
    // Byte-wise Parity — inject decoder, per-field reducers, sticky latch
    //--------------------------------------------------------------------------
    {{bytewise_parity_mod.get_inject_decode()|indent}}

    {{bytewise_parity_mod.get_field_error_reducers()|indent}}

    always_ff {{get_always_ff_event(cpuif.reset)}} begin
        if({{get_resetsignal(cpuif.reset)}}) begin
            field_parity_error <= '0;
        end else begin
            {{bytewise_parity_mod.get_sticky_latch_block()|indent(12)}}
        end
    end
{%- endif %}
```

- [ ] **Step 9.3: Verify the generated SV compiles syntactically (best-effort)**

```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -c "
import os
from systemrdl import RDLCompiler
from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.udps import ALL_UDPS

rdlc = RDLCompiler()
for udp in ALL_UDPS:
    rdlc.register_udp(udp)
rdlc.compile_file('hdl-src/regblock_udps.rdl')
rdlc.compile_file('tests/test_parity/regblock.rdl')
root = rdlc.elaborate()
out = '/tmp/regblock_bw_full'
os.makedirs(out, exist_ok=True)
RegblockExporter().export(root, out, module_name='regblock', package_name='regblock_pkg', bytewise_parity=True)
sv = open(os.path.join(out, 'regblock.sv')).read()
assert 'field_parity_error' in sv
assert 'error_clear_i' in sv
assert 'parity_inject_sel' in sv
assert 'parity_inject_strobe' in sv
assert 'always_ff' in sv
# Spot-check the inject decoder
assert 'parity_inject_sel == 0' in sv or 'parity_inject_sel == 4\\'d0' in sv or '== 0)' in sv
print('OK')
print('--- module excerpt ---')
print(sv[sv.find('field_parity_error'):sv.find('field_parity_error')+800])
"
```

Expected: prints `OK` and the module excerpt shows the new logic.

If you have a SystemVerilog linter or simulator handy, also run a parse-only pass:
```bash
# Verilator parse-only example (skip if Verilator not available)
verilator --lint-only /tmp/regblock_bw_full/regblock_pkg.sv /tmp/regblock_bw_full/regblock.sv 2>&1 | head -30
```

- [ ] **Step 9.4: Commit**

```bash
git add src/peakrdl_regblock/exporter.py src/peakrdl_regblock/module_tmpl.sv
git commit -m "Emit bytewise-parity top-level ports and sticky latch"
```

---

## Task 10: Emit package-side `localparam` enumerations

**Files:**
- Modify: `src/peakrdl_regblock/parity.py` (add a `BytewiseParityPackageGenerator`)
- Modify: `src/peakrdl_regblock/exporter.py` (wire it into context)
- Modify: `src/peakrdl_regblock/package_tmpl.sv` (call it)

- [ ] **Step 10.1: Add the package generator**

Append to `src/peakrdl_regblock/parity.py`:

```python


class BytewiseParityPackageGenerator:
    """Emits the parity-related localparam declarations + comment table for the package."""

    def __init__(self, exp: 'RegblockExporter') -> None:
        self.exp = exp

    @property
    def ds(self) -> 'DesignState':
        return self.exp.ds

    def get_implementation(self) -> str:
        if not self.ds.has_bytewise_parity:
            return ""
        n_fields = len(self.ds.parity_fields)
        n_bits = len(self.ds.parity_bits)
        lines = [
            f"// Byte-wise parity enumeration (generated by --parity-byte)",
            f"localparam int N_PARITY_FIELDS = {n_fields};",
            f"localparam int N_PARITY_BITS   = {n_bits};",
            "",
            "// Per-field error indices into field_parity_error[]:",
        ]
        for (node, _bc, ferr_idx, _fp) in self.ds.parity_fields:
            name = parity_path_id(self.ds.top_node, node)
            lines.append(f"localparam int FERR_IDX_{name} = {ferr_idx};")
        lines.append("")
        lines.append("// Per-parity-bit injection indices into parity_inject_sel:")
        for (node, byte, lo, hi, pinj_idx, _ferr_idx) in self.ds.parity_bits:
            name = parity_path_id(self.ds.top_node, node, byte=byte)
            lines.append(
                f"localparam int PINJ_IDX_{name} = {pinj_idx};"
                f"  // covers field bits [{hi}:{lo}]"
            )
        lines.append("")
        lines.append(f"// Reverse mapping: which field does each parity bit belong to?")
        if n_bits > 0:
            entries = ", ".join(str(e[5]) for e in self.ds.parity_bits)
            lines.append(
                f"localparam int PINJ_TO_FERR [{n_bits}] = '{{{entries}}};"
            )
        else:
            lines.append("// (no parity bits — design is empty or only externals)")
        return "\n".join(lines)
```

- [ ] **Step 10.2: Wire the new generator into the exporter context**

Edit `src/peakrdl_regblock/exporter.py`. Update the import:

```python
from .parity import (
    ParityErrorReduceGenerator,
    BytewiseParityModuleGenerator,
    BytewiseParityPackageGenerator,
)
```

In `export()`, near the other parity generator construction:

```python
        bytewise_parity_pkg = BytewiseParityPackageGenerator(self)
```

In the context dict:

```python
            "bytewise_parity_pkg": bytewise_parity_pkg,
```

- [ ] **Step 10.3: Call it from `package_tmpl.sv`**

Edit `src/peakrdl_regblock/package_tmpl.sv`. Inside the package body (find the `package {{...}};` line and the corresponding `endpackage`), add the parity block right before `endpackage`:

```
{%- if ds.has_bytewise_parity %}

{{bytewise_parity_pkg.get_implementation()|indent}}

{%- endif %}
endpackage
```

(Replace whatever line currently has `endpackage` with the above; leave anything before that unchanged.)

- [ ] **Step 10.4: Verify package emission**

```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -c "
import os
from systemrdl import RDLCompiler
from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.udps import ALL_UDPS

rdlc = RDLCompiler()
for udp in ALL_UDPS:
    rdlc.register_udp(udp)
rdlc.compile_file('hdl-src/regblock_udps.rdl')
rdlc.compile_file('tests/test_parity/regblock.rdl')
root = rdlc.elaborate()
out = '/tmp/regblock_bw_pkg'
os.makedirs(out, exist_ok=True)
RegblockExporter().export(root, out, module_name='regblock', package_name='regblock_pkg', bytewise_parity=True)
pkg = open(os.path.join(out, 'regblock_pkg.sv')).read()
assert 'N_PARITY_FIELDS' in pkg
assert 'N_PARITY_BITS' in pkg
assert 'FERR_IDX_' in pkg
assert 'PINJ_IDX_' in pkg
assert 'PINJ_TO_FERR' in pkg
print('OK')
print('--- pkg excerpt ---')
print(pkg[pkg.find('N_PARITY_FIELDS'):pkg.find('N_PARITY_FIELDS')+1000])
"
```

Expected: prints `OK` and the package excerpt shows the localparams.

- [ ] **Step 10.5: Commit**

```bash
git add src/peakrdl_regblock/parity.py src/peakrdl_regblock/exporter.py src/peakrdl_regblock/package_tmpl.sv
git commit -m "Emit bytewise-parity localparam enumerations in package"
```

---

## Task 11: Behavioral test — new `tests/test_parity_bytewise`

**Files:**
- Create: `tests/test_parity_bytewise/__init__.py`
- Create: `tests/test_parity_bytewise/regblock.rdl`
- Create: `tests/test_parity_bytewise/testcase.py`
- Create: `tests/test_parity_bytewise/tb_template.sv`

- [ ] **Step 11.1: Create empty package marker**

```bash
mkdir -p /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock/tests/test_parity_bytewise
touch /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock/tests/test_parity_bytewise/__init__.py
```

- [ ] **Step 11.2: Write the RDL**

Create `tests/test_parity_bytewise/regblock.rdl`:

```systemrdl
addrmap top {
    default sw=rw;
    default hw=na;

    // 1) Multi-byte field with non-byte-aligned width (11 bits)
    reg multi_byte_reg {
        field { sw=rw; hw=r; } f_11bit[11] = 0;
    };

    // 2) HW-write without we (continuous load)
    reg hw_continuous_reg {
        field { sw=r; hw=w; } f_cont[16] = 0;
    };

    // 3) HW-write with we (gated)
    reg hw_gated_reg {
        field { sw=r; hw=w; we; } f_gated[8] = 0;
    };

    // 4) Compound: SW-write + HW-write + level intr + woclr
    reg compound_reg {
        field {
            sw=rw;
            hw=w;
            level intr;
            woclr;
        } f_intr[1] = 0;
    };

    // 5) Counter
    reg counter_reg {
        field { sw=rw; hw=na; counter; } f_cnt[8] = 0;
    };

    // 6) External register (parity should NOT be emitted for this)
    external reg ext_reg {
        field { sw=rw; hw=r; } f_ext[8] = 0;
    };

    multi_byte_reg     mbr   @ 0x000;
    hw_continuous_reg  hcr   @ 0x004;
    hw_gated_reg       hgr   @ 0x008;
    compound_reg       cmr   @ 0x00C;
    counter_reg        cnr   @ 0x010;
    ext_reg            extr  @ 0x014;
};
```

- [ ] **Step 11.3: Write the testcase**

Create `tests/test_parity_bytewise/testcase.py`:

```python
from ..lib.sim_testcase import SimTestCase


class TestEvenBytewise(SimTestCase):
    bytewise_parity = True

    def test_dut(self):
        self.run_test()


class TestOddBytewise(SimTestCase):
    bytewise_parity = True
    odd_parity = True

    def test_dut(self):
        self.run_test()
```

- [ ] **Step 11.4: Write the testbench**

Create `tests/test_parity_bytewise/tb_template.sv`:

```systemverilog
{% extends "lib/tb_base.sv" %}

{% block declarations %}
    logic [regblock_pkg::N_PARITY_FIELDS-1:0] field_parity_error;
    logic                                       error_clear_i = '0;
    logic [$clog2(regblock_pkg::N_PARITY_BITS)-1:0] parity_inject_sel = '0;
    logic                                       parity_inject_strobe = '0;
{% endblock %}

{% block clocking_dirs %}
        input  field_parity_error;
        output error_clear_i;
        output parity_inject_sel;
        output parity_inject_strobe;
{% endblock %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##2;

    // -------------------------------------------------------------------------
    // 1) Reset baseline — no errors
    // -------------------------------------------------------------------------
    @cb;
    assert(field_parity_error == '0)
        else $error("Reset baseline: expected all zero, got %h", field_parity_error);

    // -------------------------------------------------------------------------
    // 2) SW write to multi-byte field; observe parity follows data
    // -------------------------------------------------------------------------
    cpuif.write('h0, 32'h7FF);  // mbr.f_11bit = 0x7FF
    @cb;
    assert(field_parity_error == '0)
        else $error("After SW write: unexpected parity error %h", field_parity_error);

    // -------------------------------------------------------------------------
    // 3) Inject at every parity bit. Each must set the corresponding sticky bit.
    // -------------------------------------------------------------------------
    for (int k = 0; k < regblock_pkg::N_PARITY_BITS; k++) begin
        cb.parity_inject_sel    <= k[$clog2(regblock_pkg::N_PARITY_BITS)-1:0];
        cb.parity_inject_strobe <= 1'b1;
        @cb;
        cb.parity_inject_strobe <= 1'b0;
        @cb;  // sticky latch
        assert(field_parity_error[regblock_pkg::PINJ_TO_FERR[k]] == 1'b1)
            else $error("Injection at bit %0d did not set field_parity_error[%0d]",
                        k, regblock_pkg::PINJ_TO_FERR[k]);
        // Clear before next iteration
        cb.error_clear_i <= 1'b1;
        @cb;
        cb.error_clear_i <= 1'b0;
        @cb;
        assert(field_parity_error == '0)
            else $error("After clear: residual error %h after injection at bit %0d",
                        field_parity_error, k);
    end

    // -------------------------------------------------------------------------
    // 4) SEU on stored data (force a bit) sets the field's sticky error.
    // -------------------------------------------------------------------------
    cpuif.write('h0, 32'h0);  // restore mbr = 0
    @cb;
    assert(field_parity_error == '0);

`ifdef XILINX_XSIM
    assign dut.field_storage.mbr.f_11bit.value[0] = 1'b1;
    deassign dut.field_storage.mbr.f_11bit.value[0];
`else
    force dut.field_storage.mbr.f_11bit.value[0] = 1'b1;
    release dut.field_storage.mbr.f_11bit.value[0];
`endif
    @cb;
    @cb;
    assert(field_parity_error[regblock_pkg::FERR_IDX_MBR_F_11BIT] == 1'b1)
        else $error("SEU on mbr.f_11bit not detected");

    // Clearing while the SEU is gone (data was released) should leave it cleared
    cb.error_clear_i <= 1'b1;
    @cb;
    cb.error_clear_i <= 1'b0;
    @cb;
    assert(field_parity_error == '0)
        else $error("Sticky did not clear after SEU released");

{% endblock %}
```

- [ ] **Step 11.5: Run the new test (sim required)**

```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -m pytest tests/test_parity_bytewise -v
```

Expected: `TestEvenBytewise::test_dut` and `TestOddBytewise::test_dut` both pass with the configured simulator.

**If pytest is not available, or no simulator is configured and the test would skip, STOP and ask the user.** This task validates the entire feature; "skipped" is not equivalent to "passing." The user has access to the EDA environment (e.g. VCS/Verdi) and can either source the env, point you at the right `--sim-tool` argument, or run the tests themselves and report back. Do not commit until the test has actually passed.

- [ ] **Step 11.6: Commit**

```bash
git add tests/test_parity_bytewise/
git commit -m "Add bytewise-parity behavioral testbench"
```

---

## Task 12: Skip parity emission for fields under external addressable components

**Files:**
- Modify: `src/peakrdl_regblock/scan_design.py`

The existing `enter_Component` (lines 65-81) already returns `WalkerAction.SkipDescendants` for external nodes — fields beneath them are never visited. Verify this behavior is preserved and add a defensive assertion so a future refactor cannot silently break it.

- [ ] **Step 12.1: Add an explicit defense to `_record_bytewise_field`**

Edit `src/peakrdl_regblock/scan_design.py`. In `_record_bytewise_field` (added in Task 4), add at the top of the method:

```python
        # Defense: external descendants must already be skipped by enter_Component.
        # Keep this assertion to make the contract explicit.
        n = node.parent
        while n is not None and n != self.top_node:
            assert not n.external, (
                f"Field '{node.inst_name}' lives beneath an external component "
                f"'{n.inst_name}' but reached the bytewise parity scanner. "
                f"DesignScanner.enter_Component should have skipped it."
            )
            n = n.parent
```

- [ ] **Step 12.2: Add a unit test that verifies external skip**

Append to `tests/unit/test_parity_scan.py`:

```python


def test_external_register_is_skipped(tmp_path):
    """An external register's fields must not appear in parity_fields."""
    root = _elaborate("tests/test_parity_bytewise/regblock.rdl")
    e = RegblockExporter()
    e.export(
        root, str(tmp_path),
        module_name="regblock", package_name="regblock_pkg",
        bytewise_parity=True,
    )
    field_names = [node.inst_name for (node, *_) in e.ds.parity_fields]
    assert "f_ext" not in field_names, \
        f"Field 'f_ext' from external reg should be skipped; got {field_names}"
```

- [ ] **Step 12.3: Run unit tests**

```bash
cd /proj_soc/user_dev/ataback/oca_hw/PeakRDL-regblock
python -m pytest tests/unit/test_parity_scan.py -v
```

Expected: all tests pass, including the new `test_external_register_is_skipped`. **If pytest is not available, STOP and ask the user.**

- [ ] **Step 12.4: Commit**

```bash
git add src/peakrdl_regblock/scan_design.py tests/unit/test_parity_scan.py
git commit -m "Defensive check: external nodes never reach bytewise parity scanner"
```

---

## Task 13: Add `CHANGE.md`

**Files:**
- Create: `CHANGE.md`

- [ ] **Step 13.1: Write the changelog**

Create `CHANGE.md` at the repo root:

```markdown
# Changes

## Parity protection
- Added `--odd-parity` flag: emit odd parity instead of even.
- Added `--parity-byte` flag: byte-wise per-field parity storage with continuous comparator,
  per-field sticky error vector output, transient single-bit injection port for self-test,
  and a shared `error_clear_i` input to clear all sticky error bits.
- Existing `paritycheck` RDL property continues to work unchanged when `--parity-byte` is not set.
```

- [ ] **Step 13.2: Commit**

```bash
git add CHANGE.md
git commit -m "Add CHANGE.md"
```

---

## Self-Review Checklist (already applied; here for reference)

- **Spec coverage:**
  - Section 3.1 `--odd-parity` → Tasks 1, 2.
  - Section 3.2 `--parity-byte` → Tasks 3-10.
  - Section 4 byte-LSB tiling → Tasks 4 (`_record_bytewise_field`), 7 (template slicing).
  - Section 5.1 atomic load → Task 7 (load_next assignments).
  - Section 5.2 update-only-on-storage-update → Task 7 (parity rides `load_next_c`).
  - Section 5.3 comparator + sticky → Task 7 (combo) + Task 9 (sticky always_ff).
  - Section 5.4 reset → Task 7 (reset branch of `always_ff`).
  - Section 5.5 external skip → Task 12.
  - Section 6.1-6.2 enumerations → Task 10.
  - Section 6.3 typical usage → covered by Task 11 testbench.
  - Section 6.4 transient injection → Task 7 (mismatch XOR with `inject_hit`) + Task 8 (decoder).
  - Section 7.1 CHANGE.md → Task 13.
  - Section 8 backwards compat → Task 1, Task 2 (legacy intact, polarity threaded).
  - Section 9 testing → Task 11 (behavioral) + Tasks 4, 5, 12 (Python unit tests).

- **Placeholder scan:** No TODO/TBD/"add appropriate" — every step has explicit code or an explicit verification command.

- **Type/naming consistency:**
  - `bytewise_parity` (kwarg) ↔ `--parity-byte` (CLI) ↔ `parity_byte` (argparse attr) — confirmed mapping.
  - `field_parity_error`, `error_clear_i`, `parity_inject_sel`, `parity_inject_strobe` consistent across spec, exporter port list, module template, and testbench.
  - `parity_path_id`, `get_parity_byte_storage_identifier`, `get_parity_byte_mismatch_identifier`, `get_parity_byte_inject_hit_identifier` consistent across `parity.py`, `field_logic/__init__.py`, and the templates.
  - `parity_fields` / `parity_bits` tuple shapes consistent (see comment in Task 3 Step 3.1 and consumer code in Tasks 8, 10, 12).

---

## Notes for the executor

- **Run all `git commit` commands without `--no-verify`.** The repo has no pre-commit hooks today, but if one is added, fix the issue rather than skipping.
- **No Co-Authored-By lines.** Per the user's global preference, commit messages contain only the engineer's intent, no AI attribution.
- **Sim-dependent steps (Task 11 Step 11.5).** If the simulator isn't configured, that test will skip; commit anyway and note the skip.
- **Frequent commits.** Each task ends with a commit. Don't batch.
- **Worktree.** This plan was written to be executed in the same checkout as the spec. Use a feature branch (e.g. `bytewise-parity`) if you prefer — `git checkout -b bytewise-parity` before Task 1.
