{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // Test 1: Broadcast to entire array
    cpuif.write('h20, 32'hAA_BB_CC_DD);
    @cb;

    // Verify all 4 array elements were updated
    assert(cb.hwif_out.reg_array[0].f.value == 8'hDD)
        else $error("reg_array[0].f expected 0xDD, got 0x%0x", cb.hwif_out.reg_array[0].f.value);
    assert(cb.hwif_out.reg_array[1].f.value == 8'hDD)
        else $error("reg_array[1].f expected 0xDD, got 0x%0x", cb.hwif_out.reg_array[1].f.value);
    assert(cb.hwif_out.reg_array[2].f.value == 8'hDD)
        else $error("reg_array[2].f expected 0xDD, got 0x%0x", cb.hwif_out.reg_array[2].f.value);
    assert(cb.hwif_out.reg_array[3].f.value == 8'hDD)
        else $error("reg_array[3].f expected 0xDD, got 0x%0x", cb.hwif_out.reg_array[3].f.value);

    // Verify readback from all elements
    cpuif.assert_read('h00, 32'h00_00_00_DD);
    cpuif.assert_read('h04, 32'h00_00_00_DD);
    cpuif.assert_read('h08, 32'h00_00_00_DD);
    cpuif.assert_read('h0C, 32'h00_00_00_DD);

    // Test 2: Write different values to individual array elements
    cpuif.write('h00, 32'h00_00_00_11);
    cpuif.write('h04, 32'h00_00_00_22);
    cpuif.write('h08, 32'h00_00_00_33);
    cpuif.write('h0C, 32'h00_00_00_44);
    @cb;

    cpuif.assert_read('h00, 32'h00_00_00_11);
    cpuif.assert_read('h04, 32'h00_00_00_22);
    cpuif.assert_read('h08, 32'h00_00_00_33);
    cpuif.assert_read('h0C, 32'h00_00_00_44);

    // Test 3: Another full array broadcast
    cpuif.write('h20, 32'hFF_EE_DD_CC);
    @cb;

    // All elements should have new value
    cpuif.assert_read('h00, 32'h00_00_00_CC);
    cpuif.assert_read('h04, 32'h00_00_00_CC);
    cpuif.assert_read('h08, 32'h00_00_00_CC);
    cpuif.assert_read('h0C, 32'h00_00_00_CC);

{% endblock %}
