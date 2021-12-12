{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    //--------------------------------------------------------------------------
    // Test incrthreshold = true; incrthreshold = true;
    //--------------------------------------------------------------------------
    cpuif.assert_read('h0, 'h0);

    fork
        begin
            forever begin
                @cb;
                if(cb.hwif_out.threshold_via_bool.count.value == 0)
                    assert(cb.hwif_out.threshold_via_bool.count.decrthreshold == 1'b1);
                else
                    assert(cb.hwif_out.threshold_via_bool.count.decrthreshold == 1'b0);

                if(cb.hwif_out.threshold_via_bool.count.value == 15)
                    assert(cb.hwif_out.threshold_via_bool.count.incrthreshold == 1'b1);
                else
                    assert(cb.hwif_out.threshold_via_bool.count.incrthreshold == 1'b0);
            end
        end

        begin
            @cb;
            cb.hwif_in.threshold_via_bool.count.incr <= '1;
            repeat(32) @cb;
            cb.hwif_in.threshold_via_bool.count.incr <= '0;
            cb.hwif_in.threshold_via_bool.count.decr <= '1;
            repeat(32) @cb;
            cb.hwif_in.threshold_via_bool.count.decr <= '0;
            @cb;
            @cb;
        end
    join_any
    disable fork;

    //--------------------------------------------------------------------------
    // Test incrthreshold = 10; incrthreshold = 5;
    //--------------------------------------------------------------------------
    cpuif.assert_read('h4, 'h0);

    fork
        begin
            forever begin
                @cb;
                if(cb.hwif_out.threshold_via_const.count.value <= 5)
                    assert(cb.hwif_out.threshold_via_const.count.decrthreshold == 1'b1);
                else
                    assert(cb.hwif_out.threshold_via_const.count.decrthreshold == 1'b0);

                if(cb.hwif_out.threshold_via_const.count.value >= 10)
                    assert(cb.hwif_out.threshold_via_const.count.incrthreshold == 1'b1);
                else
                    assert(cb.hwif_out.threshold_via_const.count.incrthreshold == 1'b0);
            end
        end

        begin
            @cb;
            cb.hwif_in.threshold_via_const.count.incr <= '1;
            repeat(32) @cb;
            cb.hwif_in.threshold_via_const.count.incr <= '0;
            cb.hwif_in.threshold_via_const.count.decr <= '1;
            repeat(32) @cb;
            cb.hwif_in.threshold_via_const.count.decr <= '0;
            @cb;
            @cb;
        end
    join_any
    disable fork;

    //--------------------------------------------------------------------------
    // Test incrthreshold = ref; incrthreshold =ref;
    //--------------------------------------------------------------------------
    cpuif.assert_read('h8, 'h0);

    fork
        begin
            forever begin
                @cb;
                if(cb.hwif_out.threshold_via_ref.count.value <= 4)
                    assert(cb.hwif_out.threshold_via_ref.count.decrthreshold == 1'b1);
                else
                    assert(cb.hwif_out.threshold_via_ref.count.decrthreshold == 1'b0);

                if(cb.hwif_out.threshold_via_ref.count.value >= 11)
                    assert(cb.hwif_out.threshold_via_ref.count.incrthreshold == 1'b1);
                else
                    assert(cb.hwif_out.threshold_via_ref.count.incrthreshold == 1'b0);
            end
        end

        begin
            @cb;
            cb.hwif_in.threshold_via_ref.count.incr <= '1;
            repeat(32) @cb;
            cb.hwif_in.threshold_via_ref.count.incr <= '0;
            cb.hwif_in.threshold_via_ref.count.decr <= '1;
            repeat(32) @cb;
            cb.hwif_in.threshold_via_ref.count.decr <= '0;
            @cb;
            @cb;
        end
    join_any
    disable fork;


{% endblock %}
