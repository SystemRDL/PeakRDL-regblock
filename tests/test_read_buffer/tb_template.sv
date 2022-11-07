{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    cb.hwif_in.incr_en <= '1;
    cb.hwif_in.trigger_sig_n <= '1;
    ##1;
    cb.rst <= '0;
    ##1;

    //--------------------------------------------------------------------------
    // Wide registers
    //--------------------------------------------------------------------------

    // reg1
    // expect to read all counter values atomically
    begin
        logic [7:0] subword;
        logic [31:0] rdata;
        logic [2:0] fdata;
        cpuif.read('h0, subword);
        fdata = subword[2:0];
        rdata = {10{fdata}};
        assert(subword == rdata[7:0]);

        cpuif.assert_read('h1, rdata[15:8]);
        cpuif.assert_read('h2, rdata[23:16]);
        cpuif.assert_read('h3, rdata[31:24]);
    end

    // reg1_msb0
    // expect to read all counter values atomically
    begin
        logic [7:0] subword;
        logic [31:0] rdata;
        logic [2:0] fdata;
        cpuif.read('h4, subword);
        fdata = subword[3:1];
        rdata = {10{fdata}} << 1;
        assert(subword == rdata[7:0]);

        cpuif.assert_read('h5, rdata[15:8]);
        cpuif.assert_read('h6, rdata[23:16]);
        cpuif.assert_read('h7, rdata[31:24]);
    end

    cb.hwif_in.incr_en <= '0;
    @cb;

    // check that msb0 ordering is correct
    begin
        logic [7:0] subword;
        logic [31:0] rdata;
        logic [2:0] fdata;
        cpuif.read('h0, subword);
        fdata = subword[2:0];
        rdata = {10{fdata}};
        assert(subword == rdata[7:0]);

        cpuif.assert_read('h1, rdata[15:8]);
        cpuif.assert_read('h2, rdata[23:16]);
        cpuif.assert_read('h3, rdata[31:24]);


        fdata = {<<{fdata}};
        rdata = {10{fdata}} << 1;
        cpuif.assert_read('h4, rdata[7:0]);
        cpuif.assert_read('h5, rdata[15:8]);
        cpuif.assert_read('h6, rdata[23:16]);
        cpuif.assert_read('h7, rdata[31:24]);
    end

    cb.hwif_in.incr_en <= '1;

    // reg2
    // read-clear
    repeat(2) begin
        logic [7:0] subword;
        logic [4:0] fdata;
        logic [31:0] rdata;

        cpuif.read('h8, subword);
        rdata[7:0] = subword;
        cpuif.read('h9, subword);
        rdata[15:8] = subword;
        cpuif.read('hA, subword);
        rdata[23:16] = subword;
        cpuif.read('hB, subword);
        rdata[31:24] = subword;

        fdata = rdata[4:0];
        assert(rdata[14:10] == fdata);
        assert(rdata[26:22] == fdata);
        assert(rdata[31:27] == fdata);
    end


    //--------------------------------------------------------------------------
    // Alternate Triggers
    //--------------------------------------------------------------------------

    // Trigger via another register
    // g1
    begin
        logic [7:0] rdata;
        cpuif.read('hC, rdata);
        cpuif.assert_read('hD, rdata);
    end

    // g2
    begin
        logic [7:0] rdata1;
        logic [7:0] rdata2;
        cpuif.read('h10, rdata1);
        cpuif.read('h11, rdata2);
        cpuif.assert_read('h12, rdata1);
        cpuif.assert_read('h13, rdata2);
    end

    // triger from signal
    // g3
    cb.hwif_in.g3_r1.f1.next <= 'hAB;
    cb.hwif_in.g3_r2.f1.next <= 'hCD;
    cb.hwif_in.trigger_sig <= '1;
    cb.hwif_in.trigger_sig_n <= '0;
    @cb;
    cb.hwif_in.g3_r1.f1.next <= 'h00;
    cb.hwif_in.g3_r2.f1.next <= 'h00;
    cb.hwif_in.trigger_sig <= '0;
    cb.hwif_in.trigger_sig_n <= '1;
    @cb;
    cpuif.assert_read('h14, 'hAB);
    cpuif.assert_read('h15, 'hCD);

    // trigger from field/propref
    // g4
    begin
        logic [7:0] rdata;
        cpuif.write('h16, 'h1);
        repeat(5) @cb;
        cpuif.read('h17, rdata);
        repeat(5) @cb;
        cpuif.assert_read('h18, rdata - 1); // swmod happens one cycle earlier, so count is -1
    end

{% endblock %}
