from systemrdl import RDLCompiler

from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.cpuif.passthrough import PassthroughCpuif
from peakrdl_regblock.udps import ALL_UDPS


def test_external_block_at_address_space_end_omits_upper_bound(tmp_path):
    rdl = tmp_path / 'top.rdl'
    rdl.write_text('''addrmap top {
        reg r_t { field { sw = rw; hw = r; } f[31:0] = 0; };
        regfile tbl_t { r_t word[1024]; };
        r_t r0 @ 0x0;
        external tbl_t tbl @ 0x1000;
    };''', encoding='utf-8')
    compiler = RDLCompiler()
    for udp in ALL_UDPS:
        compiler.register_udp(udp, soft=False)
    compiler.compile_file(str(rdl))
    RegblockExporter().export(compiler.elaborate(), str(tmp_path), cpuif_cls=PassthroughCpuif)
    rtl = (tmp_path / 'top.sv').read_text(encoding='utf-8')
    for address in ('cpuif_addr', 'rd_mux_addr'):
        assert f'{address} >=' in rtl
        assert f'{address} <=' not in rtl
