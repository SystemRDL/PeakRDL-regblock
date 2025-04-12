{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // Enable all interrupts
    cpuif.write('h100, 'h1FF); // ctrl_enable
    cpuif.write('h104, 'h000); // ctrl_mask
    cpuif.write('h108, 'h1FF); // ctrl_haltenable
    cpuif.write('h10C, 'h000); // ctrl_haltmask
    cpuif.write('h110, 'h0);   // ctrl_we
    cpuif.write('h114, 'h3);   // ctrl_wel

    //--------------------------------------------------------------------------
    // Test level_irqs_1
    cpuif.assert_read('h0, 'h000);
    assert(cb.hwif_out.level_irqs_1.intr == 1'b0);
    cb.hwif_in.level_irqs_1.irq0.next <= 'h0F;
    @cb;
    cb.hwif_in.level_irqs_1.irq0.next <= 'h00;
    cpuif.assert_read('h0, 'h00F);
    assert(cb.hwif_out.level_irqs_1.intr == 1'b1);
    cpuif.write('h0, 'h3);
    cpuif.assert_read('h0, 'h00C);
    assert(cb.hwif_out.level_irqs_1.intr == 1'b1);
    cpuif.write('h0, 'hC);
    cpuif.assert_read('h0, 'h000);
    assert(cb.hwif_out.level_irqs_1.intr == 1'b0);

    cb.hwif_in.level_irqs_1.irq1.next <= 'b1;
    @cb;
    cb.hwif_in.level_irqs_1.irq1.next <= 'b0;
    cpuif.assert_read('h0, 'h100);
    assert(cb.hwif_out.level_irqs_1.intr == 1'b1);
    cpuif.write('h0, 'h100);
    @cb;
    assert(cb.hwif_out.level_irqs_1.intr == 1'b0);
    cpuif.assert_read('h0, 'h0);

    cb.hwif_in.level_irqs_1.irq1.next <= 'b1;
    cpuif.assert_read('h0, 'h100);
    assert(cb.hwif_out.level_irqs_1.intr == 1'b1);
    cpuif.write('h0, 'h100);
    cpuif.assert_read('h0, 'h100);
    assert(cb.hwif_out.level_irqs_1.intr == 1'b1);
    cb.hwif_in.level_irqs_1.irq1.next <= 'b0;
    cpuif.assert_read('h0, 'h100);
    assert(cb.hwif_out.level_irqs_1.intr == 1'b1);
    cpuif.write('h0, 'h100);
    cpuif.assert_read('h0, 'h000);
    assert(cb.hwif_out.level_irqs_1.intr == 1'b0);

    //--------------------------------------------------------------------------
    // Test level_irqs_2
    cpuif.assert_read('h4, 'h000);
    assert(cb.hwif_out.level_irqs_2.intr == 1'b0);
    assert(cb.hwif_out.level_irqs_2.halt == 1'b0);
    cb.hwif_in.level_irqs_2.irq0.next <= 'h0F;
    @cb;
    cb.hwif_in.level_irqs_2.irq0.next <= 'h00;
    cpuif.assert_read('h4, 'h00F);
    assert(cb.hwif_out.level_irqs_2.intr == 1'b1);
    assert(cb.hwif_out.level_irqs_2.halt == 1'b1);
    cpuif.write('h100, 'h0); // ctrl_enable
    @cb;
    assert(cb.hwif_out.level_irqs_2.intr == 1'b0);
    assert(cb.hwif_out.level_irqs_2.halt == 1'b1);
    cpuif.write('h108, 'h0); // ctrl_haltenable
    @cb;
    assert(cb.hwif_out.level_irqs_2.intr == 1'b0);
    assert(cb.hwif_out.level_irqs_2.halt == 1'b0);
    cpuif.write('h100, 'h1FF); // ctrl_enable
    cpuif.write('h108, 'h1FF); // ctrl_haltenable
    @cb;
    assert(cb.hwif_out.level_irqs_2.intr == 1'b1);
    assert(cb.hwif_out.level_irqs_2.halt == 1'b1);
    cpuif.write('h4, 'h1FF);
    @cb;
    assert(cb.hwif_out.level_irqs_2.intr == 1'b0);
    assert(cb.hwif_out.level_irqs_2.halt == 1'b0);

    //--------------------------------------------------------------------------
    // Test level_irqs_3
    cpuif.assert_read('h8, 'h000);
    assert(cb.hwif_out.level_irqs_3.intr == 1'b0);
    assert(cb.hwif_out.level_irqs_3.halt == 1'b0);
    cb.hwif_in.level_irqs_3.irq0.next <= 'h0F;
    @cb;
    cb.hwif_in.level_irqs_3.irq0.next <= 'h00;
    cpuif.assert_read('h8, 'h00F);
    assert(cb.hwif_out.level_irqs_3.intr == 1'b1);
    assert(cb.hwif_out.level_irqs_3.halt == 1'b1);
    cpuif.write('h104, 'h0F); // ctrl_mask
    @cb;
    assert(cb.hwif_out.level_irqs_3.intr == 1'b0);
    assert(cb.hwif_out.level_irqs_3.halt == 1'b1);
    cpuif.write('h10C, 'hF); // ctrl_haltmask
    @cb;
    assert(cb.hwif_out.level_irqs_3.intr == 1'b0);
    assert(cb.hwif_out.level_irqs_3.halt == 1'b0);
    cpuif.write('h104, 'h0); // ctrl_mask
    cpuif.write('h10C, 'h0); // ctrl_haltmask
    @cb;
    assert(cb.hwif_out.level_irqs_3.intr == 1'b1);
    assert(cb.hwif_out.level_irqs_3.halt == 1'b1);

    //--------------------------------------------------------------------------
    // Test level_irqs with we
    cpuif.assert_read('h10, 'h000);
    assert(cb.hwif_out.level_irqs_we.intr == 1'b0);
    cb.hwif_in.level_irqs_we.irq0.next <= 'h0F;
    @cb;
    cb.hwif_in.level_irqs_we.irq0.next <= 'h00;
    assert(cb.hwif_out.level_irqs_we.intr == 1'b0);
    cpuif.assert_read('h10, 'h000);
    cpuif.write('h110, 'h1); // enable ctrl_we
    @cb;
    cpuif.assert_read('h110, 'h1);
    assert(cb.hwif_out.level_irqs_we.intr == 1'b0);
    cb.hwif_in.level_irqs_we.irq0.next <= 'h0F;
    @cb;
    cpuif.assert_read('h10, 'h00F);
    assert(cb.hwif_out.level_irqs_we.intr == 1'b1);
    cpuif.write('h110, 'h0); // disable ctrl_we
    cpuif.write('h10, 'h1FF);
    @cb;
    assert(cb.hwif_out.level_irqs_we.intr == 1'b0);
    cpuif.assert_read('h10, 'h000);
    cb.hwif_in.level_irqs_we.irq0.next <= 'h00;

    //--------------------------------------------------------------------------
    // Test level_irqs with wel
    cpuif.assert_read('h14, 'h000);
    assert(cb.hwif_out.level_irqs_wel.intr == 1'b0);
    cb.hwif_in.level_irqs_wel.irq0.next <= 'h0F;
    @cb;
    cb.hwif_in.level_irqs_wel.irq0.next <= 'h00;
    cpuif.assert_read('h14, 'h000);
    assert(cb.hwif_out.level_irqs_wel.intr == 1'b0);
    cpuif.write('h114, 'h2); // enable ctrl_we
    @cb;
    cpuif.assert_read('h14, 'h000);
    assert(cb.hwif_out.level_irqs_wel.intr == 1'b0);
    cb.hwif_in.level_irqs_wel.irq0.next <= 'h0F;
    @cb;
    cpuif.assert_read('h14, 'h00F);
    assert(cb.hwif_out.level_irqs_wel.intr == 1'b1);
    cpuif.write('h114, 'h3); // disable ctrl_we
    cpuif.write('h14, 'h1FF);
    @cb;
    assert(cb.hwif_out.level_irqs_wel.intr == 1'b0);
    cpuif.assert_read('h14, 'h000);
    cb.hwif_in.level_irqs_wel.irq0.next <= 'h00;

    //--------------------------------------------------------------------------
    // Test posedge_irqs
    cpuif.assert_read('h20, 'h000);
    assert(cb.hwif_out.posedge_irqs.intr == 1'b0);
    cb.hwif_in.posedge_irqs.irq1.next <= 1'b1;
    @cb;
    cpuif.assert_read('h20, 'h100);
    assert(cb.hwif_out.posedge_irqs.intr == 1'b1);
    cpuif.write('h20, 'h100);
    cpuif.assert_read('h20, 'h000);
    assert(cb.hwif_out.posedge_irqs.intr == 1'b0);
    cpuif.assert_read('h20, 'h000);

    cb.hwif_in.posedge_irqs.irq1.next <= 1'b0;
    cpuif.assert_read('h20, 'h000);
    assert(cb.hwif_out.posedge_irqs.intr == 1'b0);

    //--------------------------------------------------------------------------
    // Test negedge_irqs
    cpuif.assert_read('h30, 'h000);
    assert(cb.hwif_out.negedge_irqs.intr == 1'b0);
    cb.hwif_in.negedge_irqs.irq1.next <= 1'b1;
    @cb;
    cpuif.assert_read('h30, 'h000);
    assert(cb.hwif_out.negedge_irqs.intr == 1'b0);
    cb.hwif_in.negedge_irqs.irq1.next <= 1'b0;
    cpuif.assert_read('h30, 'h100);
    assert(cb.hwif_out.negedge_irqs.intr == 1'b1);
    cpuif.write('h30, 'h100);
    cpuif.assert_read('h30, 'h000);
    assert(cb.hwif_out.negedge_irqs.intr == 1'b0);
    cpuif.assert_read('h30, 'h000);

    //--------------------------------------------------------------------------
    // Test bothedge_irqs
    cpuif.assert_read('h40, 'h000);
    assert(cb.hwif_out.bothedge_irqs.intr == 1'b0);

    cb.hwif_in.bothedge_irqs.irq1.next <= 1'b1;
    cpuif.assert_read('h40, 'h100);
    assert(cb.hwif_out.bothedge_irqs.intr == 1'b1);
    cpuif.write('h40, 'h100);
    cpuif.assert_read('h40, 'h000);
    assert(cb.hwif_out.bothedge_irqs.intr == 1'b0);
    cpuif.assert_read('h40, 'h000);

    cb.hwif_in.bothedge_irqs.irq1.next <= 1'b0;
    cpuif.assert_read('h40, 'h100);
    assert(cb.hwif_out.bothedge_irqs.intr == 1'b1);
    cpuif.write('h40, 'h100);
    cpuif.assert_read('h40, 'h000);
    assert(cb.hwif_out.bothedge_irqs.intr == 1'b0);
    cpuif.assert_read('h40, 'h000);


    //--------------------------------------------------------------------------
    // Test top_irq
    cpuif.assert_read('h50, 'h000);
    assert(cb.hwif_out.top_irq.intr == 1'b0);

    cb.hwif_in.level_irqs_1.irq0.next <= 'h01;
    @cb;
    cb.hwif_in.level_irqs_1.irq0.next <= 'h00;
    cpuif.assert_read('h50, 'b0001);
    assert(cb.hwif_out.top_irq.intr == 1'b1);
    cpuif.write('h0, 'h01);
    cpuif.assert_read('h50, 'b0000);
    assert(cb.hwif_out.top_irq.intr == 1'b0);

    cb.hwif_in.posedge_irqs.irq0.next <= 'h01;
    @cb;
    cb.hwif_in.posedge_irqs.irq0.next <= 'h00;
    cpuif.assert_read('h50, 'b0010);
    assert(cb.hwif_out.top_irq.intr == 1'b1);
    cpuif.write('h20, 'h01);
    cpuif.assert_read('h50, 'b0000);
    assert(cb.hwif_out.top_irq.intr == 1'b0);

    cb.hwif_in.negedge_irqs.irq0.next <= 'h01;
    @cb;
    cb.hwif_in.negedge_irqs.irq0.next <= 'h00;
    @cb;
    cpuif.assert_read('h50, 'b0100);
    assert(cb.hwif_out.top_irq.intr == 1'b1);
    cpuif.write('h30, 'h01);
    cpuif.assert_read('h50, 'b0000);
    assert(cb.hwif_out.top_irq.intr == 1'b0);

    cb.hwif_in.bothedge_irqs.irq0.next <= 'h01;
    @cb;
    cb.hwif_in.bothedge_irqs.irq0.next <= 'h00;
    cpuif.assert_read('h50, 'b1000);
    assert(cb.hwif_out.top_irq.intr == 1'b1);
    cpuif.write('h40, 'h01);
    cpuif.assert_read('h50, 'b0000);
    assert(cb.hwif_out.top_irq.intr == 1'b0);

    cpuif.write('h108, 'h000); // ctrl_haltenable
    cb.hwif_in.level_irqs_2.irq0.next <= 'h01;
    @cb;
    cb.hwif_in.level_irqs_2.irq0.next <= 'h00;
    @cb;
    cpuif.assert_read('h50, 'b00000);
    assert(cb.hwif_out.top_irq.intr == 1'b0);

    cpuif.write('h108, 'h001); // ctrl_haltenable
    cpuif.assert_read('h50, 'b10000);
    assert(cb.hwif_out.top_irq.intr == 1'b1);

    cpuif.write('h4, 'h01);
    cpuif.assert_read('h50, 'b00000);
    assert(cb.hwif_out.top_irq.intr == 1'b0);

    //--------------------------------------------------------------------------
    // Test multi-bit sticky reg
    cpuif.assert_read('h60, 'h00);
    cb.hwif_in.stickyreg.stickyfield.next <= 'h12;
    @cb;
    cb.hwif_in.stickyreg.stickyfield.next <= 'h34;
    @cb;
    cb.hwif_in.stickyreg.stickyfield.next <= 'h56;
    @cb;
    cpuif.assert_read('h60, 'h12);
    cpuif.write('h60, 'h00);
    @cb;
    cb.hwif_in.stickyreg.stickyfield.next <= 'h78;
    @cb;
    cpuif.assert_read('h60, 'h56);


{% endblock %}
