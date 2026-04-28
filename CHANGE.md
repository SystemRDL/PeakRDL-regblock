# Changes

## Parity protection
- Added `--odd-parity` flag: emit odd parity instead of even.
- Added `--parity-byte` flag: byte-wise per-field parity storage with continuous comparator,
  per-field sticky error vector output, transient single-bit injection port for self-test,
  and a shared `error_clear_i` input to clear all sticky error bits.
- Existing `paritycheck` RDL property continues to work unchanged when `--parity-byte` is not set.
