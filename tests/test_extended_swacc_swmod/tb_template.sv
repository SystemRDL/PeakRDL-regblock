{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    logic [7:0] counter;
    logic [7:0] rd_data;
    logic [7:0] latched_data;
    int event_count;
    latched_data = 'x;

    ##1;
    cb.rst <= '0;
    ##1;

    // Verify that hwif gets sampled at the same cycle as rd_swacc strobe
    counter = 'h10;
    cb.hwif_in.r1.f.next <= counter;
    @cb;
    event_count = 0;
    fork
        begin
            ##0;
            forever begin
                counter++;
                cb.hwif_in.r1.f.next <= counter;
                @cb;
                if(cb.hwif_out.r1.f.rd_swacc) begin
                    latched_data = counter;
                    event_count++;
                end
            end
        end

        begin
            cpuif.read('h0, rd_data);
            @cb;
        end
    join_any
    disable fork;
    assert(rd_data == latched_data) else $error("Read returned 0x%0x but rd_swacc strobed during 0x%0x", rd_data, latched_data);
    assert(event_count == 1) else $error("Observed excess rd_swacc events: %0d", event_count);


    // Verify that hwif changes 1 cycle after wr_swacc
    fork
        begin
            ##0;
            forever begin
                assert(cb.hwif_out.r2.f.value == 20);
                if(cb.hwif_out.r2.f.wr_swacc) break;
                @cb;
            end
            @cb;
            forever begin
                assert(cb.hwif_out.r2.f.value == 21);
                assert(cb.hwif_out.r2.f.wr_swacc == 0);
                @cb;
            end
        end

        begin
            cpuif.write('h1, 21);
            @cb;
        end
    join_any
    disable fork;

{% endblock %}
