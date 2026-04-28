# Byte-wise Per-Field Parity for PeakRDL-regblock — Design Spec

**Date:** 2026-04-28
**Status:** Draft, awaiting review

## 1. Goals

Add a parity protection mode to the PeakRDL-regblock generator that:

- Stores parity bits *alongside* every storage field's data, sliced byte-wise.
- Continuously checks stored parity against stored data and exposes a per-field, sticky error vector at the top-level interface (cleared by a shared `error_clear_i` input).
- Allows transient single-bit error injection from a top-level SV port for self-test (DTTI).
- Is enabled via a CLI flag, not via SystemRDL property — the same RDL can be built with or without parity.
- Is additive: leaves the existing `paritycheck` RDL property and its single-bit per-field even-parity logic intact, so downstream consumers (and any upstream PR) keep working.

## 2. Non-goals

- Bus-side parity check/generate. Incoming SW-write and outgoing SW-read parity are handled by an external `axi_parity_manager`; this design only stores and locally checks parity.
- Lockstep replication of HW-write inputs. External concern, instantiated at the regblock boundary.
- Multi-bit injection. Odd parity only detects single-bit flips, so the injection interface is single-bit.
- Bit-position reporting on a parity error. The error output is a per-field strobe; software/external logic identifies which field via the vector index.
- Error injection via RDL-emitted CSRs. Out of scope by user preference — injection is via top-level SV port only.
- Persistent injection (corrupting the stored parity flop). Injection is transient (comparator-input only).
- **Parity protection of external registers.** External (`external` keyword) registers have no internal storage in the regblock; they hand off to user-provided storage outside. The regblock cannot protect what it does not store. External registers are skipped by the parity codegen in both legacy and new modes, matching today's behavior. See Section 5.5.

## 3. CLI flags

Two new flags on the `peakrdl regblock` subcommand. Both default off.

### 3.1 `--odd-parity`

Inverts the polarity of any parity bit emitted by the generator. Applies to **both** the legacy single-bit `paritycheck` path and the new byte-wise path.

- Without flag: `parity = ^data` (even parity, today's behavior in the legacy path).
- With flag: `parity = ~^data` (odd parity).

Threaded through `RegblockExporter.export(..., odd_parity: bool = False)` and stored on the design state object.

### 3.2 `--parity-byte`

Enables the new byte-wise per-field architecture for **every** storage field in the design. When this flag is set:

- The legacy `paritycheck` RDL property is ignored (no error, no warning — the new mode covers all fields).
- The legacy single-bit per-field parity logic is **not** emitted alongside; the new byte-wise logic replaces it.
- New top-level ports (Section 6) are added.

When the flag is *not* set, the new logic is fully absent from the generated SV. The legacy `paritycheck`-driven path emits as it does today (modulo `--odd-parity`).

Threaded through `RegblockExporter.export(..., bytewise_parity: bool = False)`.

The two flags are independent: any combination is valid.

## 4. Per-byte tiling rule (field-LSB slicing)

For each storage field of width `W`, generate `B = ceil(W/8)` parity bits. Slice the field starting from its LSB:

- `parity[0]` covers field bits `[7:0]`
- `parity[i]` covers field bits `[min(8*i+7, W-1) : 8*i]`
- The top slice may cover fewer than 8 data bits when `W` is not a multiple of 8.

Worked example — field at register bits `[13:3]` (width 11):
- `parity[0]` covers field bits `[7:0]` = register bits `[10:3]` (8 data bits).
- `parity[1]` covers field bits `[10:8]` = register bits `[13:11]` (3 data bits).

Slicing is purely in field coordinates. The field's placement within its parent register is irrelevant to the slicing rule — fields are the unit of internal reference in PeakRDL-regblock and parity stays in that frame.

## 5. Storage, comparator, update behavior

### 5.1 Atomic load invariant

The new logic preserves the existing template's invariant: storage and parity load from the same `field_combo.next` value, gated by the same `load_next_c`, in the same `always_ff` block. There is no path that updates one without the other.

For each field byte `i`:

```
field_storage.<path>.value[8*i +: w_i]  <= field_combo.<path>.next[8*i +: w_i];
field_storage.<path>.parity[i]          <= [~]^field_combo.<path>.next[8*i +: w_i];
```

(`[~]` present iff `--odd-parity`. `w_i` is the slice width — 8 for full slices, less for the top slice.)

### 5.2 Update only on actual storage update

The parity flops are gated by exactly the same `load_next_c` that gates the data flops. Whenever storage updates, parity updates with it from the same `next_c` value; otherwise neither moves. Concretely:

- **`sw=rw, hw=r`** — `load_next_c` asserts only on SW writes. Stored parity bits update only on SW writes.
- **`sw=r, hw=w` (no `we`/`wel`)** — `load_next_c` asserts every cycle (continuous load from `hwif_in.<field>.next`). Stored parity bits update every cycle, tracking the input. A SEU in either flop is detectable for the one cycle it lives in storage before the next continuous load overwrites it.
- **`sw=r, hw=w` with `we` or `wel`** — `load_next_c` asserts only when the enable is active. Stored parity updates only on those cycles.
- **Compound update paths** (e.g. `sw=rw` + `hw=w` + `level intr` + `woclr`) — parity rides the winning conditional's `next_c` atomically. The conditional priority determined by PeakRDL's existing field-logic generator decides who wins.

This invariant follows from the template structure and does not require any additional gating logic. Spec calls it out so it is explicit and preserved through any future refactor.

### 5.3 Continuous comparator and sticky error latching

The comparator is two-stage: a combinational mismatch detector followed by a per-field sticky latch.

**Stage 1 — combinational mismatch.** For each field byte `i`:

```
mismatch[i] = (stored_parity[i] != [~]^stored_value[8*i +: w_i]);
```

(Section 6.4 shows the form including the injection XOR; the two are the same expression with `inject_hit[i] = 0` here.)

**Stage 2 — sticky per-field error latch.** A flop per parity-protected field:

```systemverilog
always_ff @(posedge clk) begin
    if (rst) begin
        field_parity_error[k] <= 1'b0;
    end else if (error_clear_i) begin
        field_parity_error[k] <= 1'b0;
    end else if (|mismatch[B-1:0]) begin
        field_parity_error[k] <= 1'b1;
    end
end
```

`k` is the field's flat index (Section 6). Once set, `field_parity_error[k]` stays high until `error_clear_i` is asserted. A SEU in any single parity flop or any single data flop sets the corresponding sticky bit on the cycle after the SEU appears (one extra cycle of latency vs. a pure-combinational design). The combinational `mismatch` is internal — only the sticky `field_parity_error[k]` is visible at the top level.

**Set/clear precedence.** If `error_clear_i` is asserted in the same cycle that a mismatch is occurring, clear wins for that cycle (bit goes to 0). On the *next* cycle, if the mismatch is still asserting, the sticky bit sets again. This is the standard sticky-status pattern — software pulses clear, then re-reads to determine whether the fault was transient or persistent.

The clear input is shared across all fields (Section 6 — single `error_clear_i` top-level port). There is no per-field clear; software clears all parity errors at once.

### 5.4 Reset behavior

On reset, parity flops are assigned the parity of the field's reset value, mirroring the existing `paritycheck` template:

```
field_storage.<path>.parity[i] <= [~]^{{reset_expr}}[8*i +: w_i];
```

`{{reset_expr}}` is the same SV expression PeakRDL already emits for the field's reset (literal value or signal reference, depending on the RDL). The XOR-reduction is part of the assignment; for literal resets the synthesizer collapses it to a constant.

The sticky `field_parity_error[k]` flop also resets to 0.

### 5.5 External registers — explicitly skipped

The `scan_design` walker already returns `WalkerAction.SkipDescendants` when it enters a node with `external = true` (used by the legacy `paritycheck` reduce generator). The new bytewise generator inherits the same skip rule:

- No `localparam` index, no `field_parity_error` bit, no `parity_inject` allocation, no entry in the report file is emitted for any field beneath an external addressable component.
- The `--parity-byte` flag has *no effect* on the SV emitted for the external register's existing `req` / `ack` / `rd_data` / `wr_data` handshake ports — those continue to be generated unchanged.
- Users who need parity on externally stored data must implement it on their side of the handshake. This typically means a small wrapper module that holds the storage, computes parity on writes, checks it on reads, and exposes its own `parity_error` to the consuming logic that the integrator can OR into the system-level fault path.

The generated `--parity-report` file (Section 6.2(c)) calls out external addressable components with a `(external — not protected)` annotation so SW/build-system tooling can flag them rather than silently miss them.

## 6. Top-level ports

When `--parity-byte` is set, the generated module gets:

```systemverilog
// Per-field sticky parity error, one bit per parity-protected field.
// Set on the cycle after a mismatch is observed; cleared by error_clear_i.
output logic [N_PARITY_FIELDS-1:0]                field_parity_error,

// Synchronous level clear, applies to all fields. Pulse for one cycle to clear.
input  logic                                       error_clear_i,

// Single-bit transient injection into the comparator.
input  logic [$clog2(N_PARITY_BITS)-1:0]          parity_inject_sel,
input  logic                                       parity_inject_strobe
```

`N_PARITY_FIELDS` and `N_PARITY_BITS` are emitted as `localparam int` in the generated SV package.

### 6.1 Flat enumerations

Two flat enumerations are emitted, ordered by depth-first walk of the addrmap (matches existing PeakRDL traversal):

- **Field index** (size `N_PARITY_FIELDS`): one entry per parity-protected field. Indexes `field_parity_error[N_PARITY_FIELDS-1:0]`.
- **Parity-bit index** (size `N_PARITY_BITS`): one entry per parity bit in the design, ordered by field index, then by byte index within the field. Drives `parity_inject_sel`.

The two enumerations are **not** the same width — `N_PARITY_BITS >= N_PARITY_FIELDS` in general, with equality only when every parity-protected field is ≤ 8 bits wide. A multi-byte field contributes one entry to `field_parity_error` and `B = ceil(W/8)` entries to `parity_inject_sel`.

### 6.2 How external logic selects an index — generated SV constants

The mapping is exposed three ways, each suited to a different consumer.

**(a) Named `localparam` constants in the generated SV package.** This is the primary, programmatic interface for external self-test SV. For every parity-protected field, the package emits both a field-error index and one parity-bit index per byte:

```systemverilog
package my_regs_pkg;
    // ... existing hwif declarations ...

    // Parity enumeration sizes
    localparam int N_PARITY_FIELDS = 17;
    localparam int N_PARITY_BITS   = 42;

    // Per-field error indices (into field_parity_error[])
    localparam int FERR_IDX_REGA_FIELDX  = 0;
    localparam int FERR_IDX_REGA_FIELDY  = 1;
    localparam int FERR_IDX_REGB_STATUS  = 2;
    // ...

    // Per-parity-bit injection indices (into parity_inject_sel)
    localparam int PINJ_IDX_REGA_FIELDX_BYTE0 = 0;
    localparam int PINJ_IDX_REGA_FIELDX_BYTE1 = 1;
    localparam int PINJ_IDX_REGA_FIELDX_BYTE2 = 2;
    localparam int PINJ_IDX_REGA_FIELDX_BYTE3 = 3;
    localparam int PINJ_IDX_REGA_FIELDY_BYTE0 = 4;
    localparam int PINJ_IDX_REGA_FIELDY_BYTE1 = 5;  // top slice, partial
    localparam int PINJ_IDX_REGB_STATUS_BYTE0 = 6;
    // ...

    // Reverse mapping: which field does each parity-bit index belong to?
    localparam int PINJ_TO_FERR [N_PARITY_BITS] = '{
        FERR_IDX_REGA_FIELDX,  // PINJ_IDX_REGA_FIELDX_BYTE0
        FERR_IDX_REGA_FIELDX,  // PINJ_IDX_REGA_FIELDX_BYTE1
        FERR_IDX_REGA_FIELDX,  // PINJ_IDX_REGA_FIELDX_BYTE2
        FERR_IDX_REGA_FIELDX,  // PINJ_IDX_REGA_FIELDX_BYTE3
        FERR_IDX_REGA_FIELDY,  // PINJ_IDX_REGA_FIELDY_BYTE0
        FERR_IDX_REGA_FIELDY,  // PINJ_IDX_REGA_FIELDY_BYTE1
        FERR_IDX_REGB_STATUS,  // PINJ_IDX_REGB_STATUS_BYTE0
        // ...
    };
endpackage
```

Identifier construction: take the dotted RDL path of the field, replace `.` with `_`, uppercase. Append `_BYTE<i>` for parity-bit constants. The codegen guarantees uniqueness (PeakRDL already enforces this for field paths in the hwif struct).

**(b) Inline SV comment table next to the localparam block,** for human browsing. Same content as (a) plus the field width and the data-bit range each parity bit covers:

```
// Field index | Path                | Width | Parity bits
// 0           | top.regA.fieldX     | 32    | 4
// 1           | top.regA.fieldY     | 11    | 2
// 2           | top.regB.status     | 6     | 1
// ...
//
// Parity-bit idx | Field idx | Byte | Covers field bits | Covers register bits
// 0              | 0         | 0    | [7:0]             | [7:0]
// 1              | 0         | 1    | [15:8]            | [15:8]
// 2              | 0         | 2    | [23:16]           | [23:16]
// 3              | 0         | 3    | [31:24]           | [31:24]
// 4              | 1         | 0    | [7:0]             | [10:3]
// 5              | 1         | 1    | [10:8]            | [13:11]    (partial slice)
// 6              | 2         | 0    | [5:0]             | [5:0]      (partial slice)
// ...
```

**(c) Optional report file** via a new `--parity-report` CLI flag (mirrors the existing `--hwif-report`). Emits a plain-text or JSON file with the same content, suitable for SW build systems that need to generate matching DTTI test loops in C.

### 6.3 Typical external usage

A self-test FSM iterates `parity_inject_sel` from `0` to `N_PARITY_BITS - 1`, pulses `parity_inject_strobe` for one cycle at each step, observes the sticky `field_parity_error` bit set on the next cycle, and pulses `error_clear_i` to reset before the next iteration:

```systemverilog
// Pseudocode in an external self-test FSM
for (int k = 0; k < my_regs_pkg::N_PARITY_BITS; k++) begin
    // Step 1: pulse injection for one cycle
    parity_inject_sel    = k[$clog2(my_regs_pkg::N_PARITY_BITS)-1:0];
    parity_inject_strobe = 1'b1;
    @(posedge clk);
    parity_inject_strobe = 1'b0;
    @(posedge clk);  // sticky bit latches on this edge

    // Step 2: verify sticky bit set for the right field
    assert (field_parity_error[my_regs_pkg::PINJ_TO_FERR[k]] === 1'b1)
        else $error("self-test failed at parity-bit index %0d", k);

    // Step 3: clear before next iteration
    error_clear_i = 1'b1;
    @(posedge clk);
    error_clear_i = 1'b0;
end
```

For per-field targeting (rather than per-parity-bit), external logic can address by name:

```systemverilog
parity_inject_sel = my_regs_pkg::PINJ_IDX_REGA_FIELDX_BYTE2;
```

and observe `field_parity_error[my_regs_pkg::FERR_IDX_REGA_FIELDX]`.

### 6.4 Transient injection semantics

When `parity_inject_strobe` is high in cycle `t`:

- The parity bit at flat index `parity_inject_sel` has its **comparator input** XOR'd with 1 during cycle `t`.
- The corresponding `mismatch[i]` is high in cycle `t`, latching `field_parity_error[k] = 1` on the cycle-`t+1` clock edge.
- The stored parity flop is **not** modified. After deasserting `parity_inject_strobe`, the combinational `mismatch` returns to 0; the sticky `field_parity_error[k]` remains set until `error_clear_i` is pulsed.

Implementation: the comparator becomes

```
mismatch[i] = (stored_parity[i] != ([~]^stored_value[8*i +: w_i] ^ inject_hit[i]));
```

where `inject_hit[i]` is a 1-cycle pulse equal to `parity_inject_strobe & (parity_inject_sel == flat_idx_of(field, i))`.

Codegen emits a one-hot decoder of `parity_inject_sel` distributed across all parity bits.

When `parity_inject_strobe` is low, all `inject_hit[i]` are 0 and the comparator behaves normally.

**Precondition:** software / external self-test logic must verify `field_parity_error == '0` *before* asserting `parity_inject_strobe`. If a real fault is already setting `field_parity_error[k]`, the injection XOR will *cancel* the underlying mismatch for the duration of the strobe — but the sticky bit is already latched, so a pre-existing error stays visible at the output. The risk is a *new* real fault that shows up during the inject window: it will be masked from the sticky latch for that cycle. This matches the canonical "verify baseline before injection" step from the OCAH parity self-test architecture. The regblock does not gate `field_parity_error` during injection — external logic owns the inject-window error masking (e.g. via a `selftest_active`-style signal in the consuming module).

## 7. Code organization

| Path | Change |
|---|---|
| `src/peakrdl_regblock/__peakrdl__.py` | Add `--odd-parity` and `--parity-byte` flags; pass through `do_export`. |
| `src/peakrdl_regblock/exporter.py` | Add `odd_parity` and `bytewise_parity` kwargs; thread to design state; new top-level port emitter. |
| `src/peakrdl_regblock/scan_design.py` | Build the parity-protected-fields list and flat parity-bit enumeration when `bytewise_parity` is set. |
| `src/peakrdl_regblock/parity.py` | Keep `ParityErrorReduceGenerator` (legacy). Add new generators for byte-wise parity (storage, comparator, injection decode, error fan-out). |
| `src/peakrdl_regblock/field_logic/templates/field_storage.sv` | Extend Jinja with new branches gated on `ds.has_bytewise_parity`. The legacy `paritycheck` branches stay; they are mutually exclusive at codegen time (legacy fires only when `not ds.has_bytewise_parity`). |
| `src/peakrdl_regblock/field_logic/generators.py` | Emit the byte-wise `parity` and per-byte `mismatch` struct members on parity-protected fields when `bytewise_parity` is set. |
| `src/peakrdl_regblock/module_tmpl.sv` | Emit the new top-level ports, package localparams, enumeration tables, and the inject one-hot decoder under `ds.has_bytewise_parity`. |
| `CHANGE.md` (new, project root) | Concise user-facing summary of what changed in this release. See Section 7.1. |

No existing files are deleted. The legacy `paritycheck` path remains as is.

### 7.1 CHANGE.md

A new top-level `CHANGE.md` is created (the project has no existing changelog file). It is **concise and simple** — bullet list under a single heading, user-facing language only, no implementation detail. Sample shape:

```markdown
# Changes

## Parity protection
- Added `--odd-parity` flag: emit odd parity instead of even.
- Added `--parity-byte` flag: byte-wise per-field parity storage with continuous comparator,
  per-field sticky error vector output, transient single-bit injection port for self-test,
  and a shared `error_clear_i` input to clear all sticky error bits.
- Existing `paritycheck` RDL property continues to work unchanged when `--parity-byte` is not set.
```

Future work in this repo appends to the same file.

## 8. Backward compatibility

- Without either new flag, generated SV is bit-identical to today.
- With `--odd-parity` alone, the only diff is `^` → `~^` on parity assignments and on comparator XOR-reductions inside the legacy `paritycheck` branches.
- With `--parity-byte`, the new architecture replaces legacy parity for *all* storage fields. Designs that relied on `paritycheck` for selective protection should migrate to the new flag (which protects everything) or stay on the legacy path.
- `paritycheck` RDL property remains valid in both modes; it is silently ignored when `--parity-byte` is set.

## 9. Testing

- `tests/test_parity` (existing, legacy) continues to run and pass unchanged.
- `tests/test_parity` re-run with `--odd-parity` to validate the inverter — expect existing assertions to pass against complemented parity values.
- New `tests/test_parity_bytewise` test bench covering, at minimum:
  1. Multi-byte field with non-byte-aligned width (e.g. width 11) — parity bit count, slicing, comparator logic.
  2. SW-write to a `sw=rw, hw=r` field — parity updates only on SW write.
  3. HW-write `sw=r, hw=w` without `we`/`wel` — parity tracks `hwif_in.<field>.next` every cycle.
  4. HW-write `sw=r, hw=w` with `we` — parity updates only on cycles where `we` is asserted.
  5. Compound field (`sw=rw, hw=w, level intr, woclr`) — parity rides the winning update path.
  6. Counter field — parity tracks counter storage.
  7. Byte-strobed partial SW write — unstrobed bytes' parity bits unchanged.
  8. Reset — all parity flops at parity-of-reset-value, all sticky error bits 0, no errors.
  9. Injection at every flat parity-bit index — sticky `field_parity_error[k]` sets one cycle after strobe, no other bits set, stored parity unchanged after strobe deasserts.
  10. Sticky behavior — single-cycle injection sets the sticky bit and it stays set until `error_clear_i` is pulsed; bit re-asserts after clear if mismatch is still present.
  11. `error_clear_i` precedence — clearing while a mismatch is asserting drops the bit for one cycle then it re-sets next cycle (persistent fault); clearing without active mismatch keeps it cleared (transient fault).
  12. External register present in design — generation does not emit parity logic for fields under the external subtree; non-external fields elsewhere protected normally.
  13. Both flags together (`--odd-parity --parity-byte`) — polarity correctly applied throughout.
- Reference-model checking: a Python parity model walks the same enumeration and confirms expected `field_parity_error` and stored-parity values.

## 10. Open items / future work

- Naming: `--parity-byte` is a placeholder; pick a final name before merging (`--bytewise-parity`, `--storage-parity`, etc.).
- Whether `--parity-report` should default to JSON, plain text, or both. (Section 6.2(c).)
- Whether to add a `--parity-byte` per-block override (e.g. exclude specific addrmap regions). Out of scope for this spec.
