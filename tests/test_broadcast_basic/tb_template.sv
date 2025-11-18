{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // Test 1: Write to broadcaster should update all targets
    cpuif.write('h10, 32'hAA_BB_CC_DD);
    @cb;

    // Verify all target registers were updated
    assert(cb.hwif_out.rega.f.value == 8'hDD)
        else $error("rega.f expected 0xDD, got 0x%0x", cb.hwif_out.rega.f.value);
    assert(cb.hwif_out.regb.f.value == 8'hDD)
        else $error("regb.f expected 0xDD, got 0x%0x", cb.hwif_out.regb.f.value);
    assert(cb.hwif_out.regc.f.value == 8'hDD)
        else $error("regc.f expected 0xDD, got 0x%0x", cb.hwif_out.regc.f.value);

    // Verify values can be read back from targets
    cpuif.assert_read('h0, 32'h00_00_00_DD);
    cpuif.assert_read('h4, 32'h00_00_00_DD);
    cpuif.assert_read('h8, 32'h00_00_00_DD);

    // Test 2: Individual writes to targets still work
    cpuif.write('h0, 32'h00_00_00_11);
    cpuif.write('h4, 32'h00_00_00_22);
    cpuif.write('h8, 32'h00_00_00_33);
    @cb;

    cpuif.assert_read('h0, 32'h00_00_00_11);
    cpuif.assert_read('h4, 32'h00_00_00_22);
    cpuif.assert_read('h8, 32'h00_00_00_33);

    // Test 3: Broadcast write with different value
    cpuif.write('h10, 32'h12_34_56_78);
    @cb;

    // All targets should have new broadcast value
    cpuif.assert_read('h0, 32'h00_00_00_78);
    cpuif.assert_read('h4, 32'h00_00_00_78);
    cpuif.assert_read('h8, 32'h00_00_00_78);

{% endblock %}
