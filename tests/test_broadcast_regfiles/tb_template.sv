{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // Test 1: Broadcast to reg_a in all regfiles
    // broadcast_all is at 0x40. reg_a is at offset 0x0 -> 0x40
    cpuif.write('h40, 32'h12_34_56_78);
    @cb;

    // Verify regfile_a.reg_a updated
    assert(cb.hwif_out.regfile_a.reg_a.f.value == 8'h78)
        else $error("regfile_a.reg_a.f expected 0x78, got 0x%0x", cb.hwif_out.regfile_a.reg_a.f.value);
    // Verify regfile_b.reg_a updated
    assert(cb.hwif_out.regfile_b.reg_a.f.value == 8'h78)
        else $error("regfile_b.reg_a.f expected 0x78, got 0x%0x", cb.hwif_out.regfile_b.reg_a.f.value);
    // Verify regfile_c.reg_a updated
    assert(cb.hwif_out.regfile_c.reg_a.f.value == 8'h78)
        else $error("regfile_c.reg_a.f expected 0x78, got 0x%0x", cb.hwif_out.regfile_c.reg_a.f.value);

    // Verify other registers NOT updated (should be default 0)
    assert(cb.hwif_out.regfile_a.reg_b.f.value == 8'h00)
        else $error("regfile_a.reg_b.f expected 0x00, got 0x%0x", cb.hwif_out.regfile_a.reg_b.f.value);

    // Test 2: Broadcast to reg_b in all regfiles
    // broadcast_all.reg_b is at 0x44
    cpuif.write('h44, 32'h87_65_43_21);
    @cb;

    // Verify regfile_a.reg_b updated
    assert(cb.hwif_out.regfile_a.reg_b.f.value == 8'h21)
        else $error("regfile_a.reg_b.f expected 0x21, got 0x%0x", cb.hwif_out.regfile_a.reg_b.f.value);
    // Verify regfile_b.reg_b updated
    assert(cb.hwif_out.regfile_b.reg_b.f.value == 8'h21)
        else $error("regfile_b.reg_b.f expected 0x21, got 0x%0x", cb.hwif_out.regfile_b.reg_b.f.value);

    // Verify reg_a still holds previous value
    assert(cb.hwif_out.regfile_a.reg_a.f.value == 8'h78)
        else $error("regfile_a.reg_a.f expected 0x78, got 0x%0x", cb.hwif_out.regfile_a.reg_a.f.value);

    // Test 3: Individual writes still work
    cpuif.write('h08, 32'hAA_BB_CC_DD); // regfile_a.reg_c
    @cb;
    assert(cb.hwif_out.regfile_a.reg_c.f.value == 8'hDD)
        else $error("regfile_a.reg_c.f expected 0xDD, got 0x%0x", cb.hwif_out.regfile_a.reg_c.f.value);
    // Should not affect others
    assert(cb.hwif_out.regfile_b.reg_c.f.value == 8'h00)
        else $error("regfile_b.reg_c.f expected 0x00, got 0x%0x", cb.hwif_out.regfile_b.reg_c.f.value);

    // Test 4: Broadcast to regfile array
    // broadcast_to_array is at 0x80. reg_a is at 0x80
    cpuif.write('h80, 32'hCA_FE_BA_BE);
    @cb;

    // Verify regfile_array[0].reg_a (Base 0x100)
    assert(cb.hwif_out.regfile_array[0].reg_a.f.value == 8'hBE)
        else $error("regfile_array[0].reg_a.f expected 0xBE, got 0x%0x", cb.hwif_out.regfile_array[0].reg_a.f.value);
    // Verify regfile_array[1].reg_a (Base 0x110)
    assert(cb.hwif_out.regfile_array[1].reg_a.f.value == 8'hBE)
        else $error("regfile_array[1].reg_a.f expected 0xBE, got 0x%0x", cb.hwif_out.regfile_array[1].reg_a.f.value);

    // Verify reg_b NOT updated
    assert(cb.hwif_out.regfile_array[0].reg_b.f.value == 8'h00)
        else $error("regfile_array[0].reg_b.f expected 0x00, got 0x%0x", cb.hwif_out.regfile_array[0].reg_b.f.value);

    // Readback verification
    // regfile_array[0].reg_a
    cpuif.assert_read('h100, 32'h00_00_00_BE);
    // regfile_array[1].reg_a
    cpuif.assert_read('h110, 32'h00_00_00_BE);

{% endblock %}
