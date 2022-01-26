CPU Interface Addressing
========================

TODO: write about the following:

* cpuif addressing is always 0-based (aka relative to the block's root)
* It is up to the decoder to handle the offset
* Address bus width is pruned down
* recommend that the decoder/interconnect reserve a full ^2 block of addresses to simplify decoding
