{% extends "lib/templates/tb_base.sv" %}

{% block seq %}
    logic [7:0] rd_data;
    logic [7:0] latched_data;
    int event_count;
    latched_data = 'x;

    ##1;
    cb.rst <= '0;
    ##1;

    // Verify that hwif gets sampled at the same cycle as swacc strobe
    cb.hwif_in.r1.f.value <= 'h10;
    @cb;
    event_count = 0;
    fork
        begin
            ##0;
            forever begin
                cb.hwif_in.r1.f.value <= cb.hwif_in.r1.f.value + 1;
                @cb;
                if(cb.hwif_out.r1.f.swacc) begin
                    latched_data = cb.hwif_in.r1.f.value;
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
    assert(rd_data == latched_data) else $error("Read returned 0x%0x but swacc strobed during 0x%0x", rd_data, latched_data);
    assert(event_count == 1) else $error("Observed excess swacc events: %0d", event_count);


    // Verify that hwif changes 1 cycle after swmod
    fork
        begin
            ##0;
            forever begin
                assert(hwif_out.r2.f.value == 20);
                if(hwif_out.r2.f.swmod) break;
                @cb;
            end
            @cb;
            forever begin
                assert(hwif_out.r2.f.value == 21);
                assert(hwif_out.r2.f.swmod == 0);
                @cb;
            end
        end

        begin
            cpuif.write('h1, 21);
            @cb;
        end
    join_any
    disable fork;

    // TODO: verify some other atypical swmod (onread actions)

{% endblock %}
