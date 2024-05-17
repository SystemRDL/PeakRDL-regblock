from .rw_buffering import BufferWrites, WBufferTrigger
from .rw_buffering import BufferReads, RBufferTrigger
from .extended_swacc import ReadSwacc, WriteSwacc
from .cpuif import CpuIf, AddrWidth

ALL_UDPS = [
    BufferWrites,
    WBufferTrigger,
    BufferReads,
    RBufferTrigger,
    ReadSwacc,
    WriteSwacc,
    CpuIf,
    AddrWidth,
]
