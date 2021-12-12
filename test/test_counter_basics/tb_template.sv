{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    //--------------------------------------------------------------------------
    // Test simple counters
    //--------------------------------------------------------------------------
    // up
    cpuif.assert_read('h0, 'hD, 'h000F);
    cb.hwif_in.simple.implied_up.incr <= '1;
    repeat(4) @cb;
    cb.hwif_in.simple.implied_up.incr <= '0;
    cpuif.assert_read('h0, 'h1, 'h000F);

    // up
    cpuif.assert_read('h0, 'hD0, 'h00F0);
    cb.hwif_in.simple.up.incr <= '1;
    repeat(4) @cb;
    cb.hwif_in.simple.up.incr <= '0;
    cpuif.assert_read('h0, 'h10, 'h00F0);

    // down
    cpuif.assert_read('h0, 'h400, 'h0F00);
    cb.hwif_in.simple.down.decr <= '1;
    repeat(6) @cb;
    cb.hwif_in.simple.down.decr <= '0;
    cpuif.assert_read('h0, 'hE00, 'h0F00);

    // up/down via hw
    cpuif.assert_read('h0, 'h0000, 'hF000);
    cb.hwif_in.simple.updown.incr <= '1;
    repeat(6) @cb;
    cb.hwif_in.simple.updown.incr <= '0;
    cpuif.assert_read('h0, 'h6000, 'hF000);
    cb.hwif_in.simple.updown.decr <= '1;
    repeat(6) @cb;
    cb.hwif_in.simple.updown.decr <= '0;
    cpuif.assert_read('h0, 'h0000, 'hF000);
    cb.hwif_in.simple.updown.decr <= '1;
    repeat(6) @cb;
    cb.hwif_in.simple.updown.decr <= '0;
    cpuif.assert_read('h0, 'hA000, 'hF000);
    cb.hwif_in.simple.updown.incr <= '1;
    repeat(6) @cb;
    cb.hwif_in.simple.updown.incr <= '0;
    cpuif.assert_read('h0, 'h0000, 'hF000);

    // up/down via sw
    cpuif.assert_read('h0, 'h00000, 'hF0000);
    repeat(3) cpuif.write('h0, 'h4000_0000); // incr
    cpuif.assert_read('h0, 'h90000, 'hF0000);
    repeat(3) cpuif.write('h0, 'h8000_0000); // decr
    cpuif.assert_read('h0, 'h00000, 'hF0000);
    repeat(3) cpuif.write('h0, 'h8000_0000); // decr
    cpuif.assert_read('h0, 'h70000, 'hF0000);
    repeat(3) cpuif.write('h0, 'h4000_0000); // incr
    cpuif.assert_read('h0, 'h00000, 'hF0000);

    // up/down via hw + external dynamic stepsize
    cpuif.assert_read('h0, 'h000000, 'hF00000);
    cb.hwif_in.simple.updown3.incrvalue <= 'h2;
    repeat(3) cpuif.write('h0, 'h4000_0000); // incr
    cpuif.assert_read('h0, 'h600000, 'hF00000);
    cpuif.assert_read('h4, 'h00_00); // no overflows or underflows
    cb.hwif_in.simple.updown3.decrvalue <= 'h3;
    repeat(3) cpuif.write('h0, 'h8000_0000); // decr
    cpuif.assert_read('h0, 'hD00000, 'hF00000);
    cpuif.assert_read('h4, 'h01_00); // one underflow
    cb.hwif_in.simple.updown3.incrvalue <= 'h1;
    repeat(2) cpuif.write('h0, 'h4000_0000); // incr
    cpuif.assert_read('h0, 'hF00000, 'hF00000);
    cpuif.assert_read('h4, 'h00_00); // no overflows or underflows
    repeat(1) cpuif.write('h0, 'h4000_0000); // incr
    cpuif.assert_read('h0, 'h000000, 'hF00000);
    cpuif.assert_read('h4, 'h00_01); // one overflow
    repeat(32) cpuif.write('h0, 'h4000_0000); // incr
    cpuif.assert_read('h0, 'h000000, 'hF00000);
    cpuif.assert_read('h4, 'h00_02); // overflow

    // up/down via hw + referenced dynamic stepsize
    cpuif.assert_read('h0, 'h0000000, 'hF000000);
    repeat(4) cpuif.write('h0, 'h4000_0000 + (2'h3 << 28)); // + 3
    cpuif.assert_read('h0, 'hC000000, 'hF000000);
    repeat(4) cpuif.write('h0, 'h8000_0000 + (2'h1 << 28)); // - 1
    cpuif.assert_read('h0, 'h8000000, 'hF000000);
    repeat(2) cpuif.write('h0, 'h8000_0000 + (2'h3 << 28)); // - 3
    cpuif.assert_read('h0, 'h2000000, 'hF000000);

{% endblock %}
