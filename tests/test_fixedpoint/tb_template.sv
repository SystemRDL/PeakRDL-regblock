{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // set all fields to all 1s
    cb.hwif_in.r1.f_Q32_n12.next <= '1;
    cb.hwif_in.r2.f_signed.next <= '1;
    cb.hwif_in.r2.f_no_sign.next <= '1;
    cpuif.write('h0, 64'hFFFF_FFFF_FFFF_FFFF);
    cpuif.write('h8, 64'hFFFF_FFFF_FFFF_FFFF);
    @cb;

    // Q8.8
    // verify bit range
    assert(cb.hwif_out.r1.f_Q8_8.value[7:-8] == '1);
    // verify bit width
    assert($size(cb.hwif_out.r1.f_Q8_8.value) == 16);
    // verfy unsigned
    assert(cb.hwif_out.r1.f_Q8_8.value > 0);

    // Q32.-12
    // verify bit range
    assert(cb.hwif_in.r1.f_Q32_n12.next[31:12] == '1);
    // verify bit width
    assert($size(cb.hwif_in.r1.f_Q32_n12.next) == 20);
    // verify unsigned
    assert(cb.hwif_in.r1.f_Q32_n12.next > 0);

    // SQ-8.32
    // verify bit range
    assert(cb.hwif_out.r1.f_SQn8_32.value[-9:-32] == '1);
    // verify bit width
    assert($size(cb.hwif_out.r1.f_SQn8_32.value) == 24);
    // verify signed
    assert(cb.hwif_out.r1.f_SQn8_32.value < 0);

    // SQ-6.7
    // verify bit range
    assert(cb.hwif_out.r1.f_SQn6_7.value[-7:-7] == '1);
    // verify bit width
    assert($size(cb.hwif_out.r1.f_SQn6_7.value) == 1);
    // verify signed
    assert(cb.hwif_out.r1.f_SQn6_7.value < 0);

    // 16-bit signed integer
    // verify bit range
    assert(cb.hwif_in.r2.f_signed.next[15:0] == '1);
    // verify bit width
    assert($size(cb.hwif_in.r2.f_signed.next) == 16);
    // verify signed
    assert(cb.hwif_in.r2.f_signed.next < 0);

    // 16-bit unsigned integer
    // verify bit range
    assert(cb.hwif_out.r2.f_unsigned.value[15:0] == '1);
    // verify bit width
    assert($size(cb.hwif_out.r2.f_unsigned.value) == 16);
    // verify unsigned
    assert(cb.hwif_out.r2.f_unsigned.value > 0);

    // 16-bit field (no sign)
    // verify bit range
    assert(cb.hwif_in.r2.f_no_sign.next[15:0] == '1);
    // verify bit width
    assert($size(cb.hwif_in.r2.f_no_sign.next) == 16);
    // verify unsigned (logic is unsigned in SV)
    assert(cb.hwif_in.r2.f_no_sign.next > 0);

    // verify readback
    cpuif.assert_read('h0, 64'h1FFF_FFFF_FFFF_FFFF);
    cpuif.assert_read('h8, 64'h0000_FFFF_FFFF_FFFF);

{% endblock %}
