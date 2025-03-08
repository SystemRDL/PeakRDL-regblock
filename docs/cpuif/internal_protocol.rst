.. _cpuif_protocol:

Internal CPUIF Protocol
=======================

Internally, the regblock generator uses a common CPU interface handshake
protocol. This strobe-based protocol is designed to add minimal overhead to the
regblock implementation, while also being flexible enough to support advanced
features of a variety of bus interface standards.


Signal Descriptions
-------------------

Request
^^^^^^^
cpuif_req
    When asserted, a read or write transfer will be initiated.
    Denotes that the following signals are valid: ``cpuif_addr``,
    ``cpuif_req_is_wr``, and ``cpuif_wr_data``.

    A transfer will only initiate if the relevant stall signal is not asserted.
    If stalled, the request shall be held until accepted. A request's parameters
    (type, address, etc) shall remain static throughout the stall.

cpuif_addr
    Byte-address of the transfer.

cpuif_req_is_wr
    If ``1``, denotes that the current transfer is a write. Otherwise transfer is
    a read.

cpuif_wr_data
    Data to be written for the write transfer. This signal is ignored for read
    transfers.

cpuif_wr_biten
    Active-high bit-level write-enable strobes.
    Only asserted bit positions will change the register value during a write
    transfer.

cpuif_req_stall_rd
    If asserted, and the next pending request is a read operation, then the
    transfer will not be accepted until this signal is deasserted.

cpuif_req_stall_wr
    If asserted, and the next pending request is a read operation, then the
    transfer will not be accepted until this signal is deasserted.


Read Response
^^^^^^^^^^^^^
cpuif_rd_ack
    Single-cycle strobe indicating a read transfer has completed.
    Qualifies that the following signals are valid: ``cpuif_rd_err`` and
    ``cpuif_rd_data``

cpuif_rd_err
    If set, indicates that the read transaction failed and the CPUIF logic
    should return an error response if possible.

cpuif_rd_data
    Read data. Is sampled on the same cycle that ``cpuif_rd_ack`` is asserted.

Write Response
^^^^^^^^^^^^^^
cpuif_wr_ack
    Single-cycle strobe indicating a write transfer has completed.
    Qualifies that the ``cpuif_wr_err`` signal is valid.

cpuif_wr_err
    If set, indicates that the write transaction failed and the CPUIF logic
    should return an error response if possible.


Transfers
---------

Transfers have the following characteristics:

* Only one transfer can be initiated per clock-cycle. This is implicit as there
  is only one set of request signals.
* The register block implementation shall guarantee that only one response can be
  asserted in a given clock cycle. Only one ``cpuif_*_ack`` signal can be
  asserted at a time.
* Responses shall arrive in the same order as their corresponding request was
  dispatched.


Basic Transfer
^^^^^^^^^^^^^^

Depending on the configuration of the exported register block, transfers can be
fully combinational or they may require one or more clock cycles to complete.
Both are valid and CPU interface logic shall be designed to anticipate either.

.. wavedrom::

    {
        "signal": [
            {"name": "clk",              "wave": "p...."},
            {"name": "cpuif_req",        "wave": "010.."},
            {"name": "cpuif_req_is_wr",  "wave": "x2x.."},
            {"name": "cpuif_addr",       "wave": "x2x..", "data": ["A"]},
            {},
            {"name": "cpuif_*_ack",      "wave": "010.."},
            {"name": "cpuif_*_err",      "wave": "x2x.."}
        ],
        "foot": {
            "text": "Zero-latency transfer"
        }
    }

.. wavedrom::

    {
        "signal": [
            {"name": "clk",              "wave": "p..|..."},
            {"name": "cpuif_req",        "wave": "010|..."},
            {"name": "cpuif_req_is_wr",  "wave": "x2x|..."},
            {"name": "cpuif_addr",       "wave": "x2x|...", "data": ["A"]},
            {},
            {"name": "cpuif_*_ack",      "wave": "0..|10."},
            {"name": "cpuif_*_err",      "wave": "x..|2x."}
        ],
        "foot": {
            "text": "Transfer with non-zero latency"
        }
    }


Read & Write Transactions
-------------------------

Waveforms below show the timing relationship of simple read/write transactions.
For brevity, only showing non-zero latency transfers.

.. wavedrom::

    {
        "signal": [
            {"name": "clk",              "wave": "p..|..."},
            {"name": "cpuif_req",        "wave": "010|..."},
            {"name": "cpuif_req_is_wr",  "wave": "x0x|..."},
            {"name": "cpuif_addr",       "wave": "x3x|...", "data": ["A"]},
            {},
            {"name": "cpuif_rd_ack",     "wave": "0..|10."},
            {"name": "cpuif_rd_err",     "wave": "x..|0x."},
            {"name": "cpuif_rd_data",    "wave": "x..|5x.", "data": ["D"]}
        ],
        "foot": {
            "text": "Read Transaction"
        }
    }


.. wavedrom::

    {
        "signal": [
            {"name": "clk",              "wave": "p..|..."},
            {"name": "cpuif_req",        "wave": "010|..."},
            {"name": "cpuif_req_is_wr",  "wave": "x1x|..."},
            {"name": "cpuif_addr",       "wave": "x3x|...", "data": ["A"]},
   			{"name": "cpuif_wr_data",    "wave": "x5x|...", "data": ["D"]},
            {},
            {"name": "cpuif_wr_ack",     "wave": "0..|10."},
            {"name": "cpuif_wr_err",     "wave": "x..|0x."}
        ],
        "foot": {
            "text": "Write Transaction"
        }
    }


Transaction Pipelining & Stalls
-------------------------------
If the CPU interface supports it, read and write operations can be pipelined.

.. wavedrom::

    {
        "signal": [
            {"name": "clk",              "wave": "p......"},
            {"name": "cpuif_req",        "wave": "01..0.."},
            {"name": "cpuif_req_is_wr",  "wave": "x0..x.."},
            {"name": "cpuif_addr",       "wave": "x333x..", "data": ["A1", "A2", "A3"]},
            {},
            {"name": "cpuif_rd_ack",     "wave": "0.1..0."},
            {"name": "cpuif_rd_err",     "wave": "x.0..x."},
            {"name": "cpuif_rd_data",    "wave": "x.555x.", "data": ["D1", "D2", "D3"]}
        ]
    }

It is very likely that the transfer latency of a read transaction will not
be the same as a write for a given register block configuration. Typically read
operations will be more deeply pipelined. This latency asymmetry would create a
hazard for response collisions.

In order to eliminate this hazard, additional stall signals (``cpuif_req_stall_rd``
and ``cpuif_req_stall_wr``) are provided to delay the next incoming transfer
request if necessary. When asserted, the CPU interface shall hold the next pending
request until the stall is cleared.

For non-pipelined CPU interfaces that only allow one outstanding transaction at a time,
these stall signals can be safely ignored.

In the following example, the regblock is configured such that:

* A read transaction takes 1 clock cycle to complete
* A write transaction takes 0 clock cycles to complete

.. wavedrom::

    {
        "signal": [
            {"name": "clk",                "wave": "p......."},
            {"name": "cpuif_req",          "wave": "01.....0"},
            {"name": "cpuif_req_is_wr",    "wave": "x1.0.1.x"},
            {"name": "cpuif_addr",         "wave": "x33443.x", "data": ["W1", "W2", "R1", "R2", "W3"]},
            {"name": "cpuif_req_stall_wr", "wave": "0...1.0."},
            {},
            {"name": "cpuif_rd_ack",       "wave": "0...220.", "data": ["R1", "R2"]},
            {"name": "cpuif_wr_ack",       "wave": "0220..20", "data": ["W1", "W2", "W3"]}
        ]
    }

In the above waveform, observe that:

* The ``R2`` read request is not affected by the assertion of the write stall,
  since the write stall only applies to write requests.
* The ``W3`` write request is stalled for one cycle, and is accepted once the stall is cleared.
