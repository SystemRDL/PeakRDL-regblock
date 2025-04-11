{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    logic [7:0] counter;
    logic [7:0] rd_data;
    logic [7:0] latched_data;
    int event_count;
    bit fired;
    latched_data = 'x;

    ##1;
    cb.rst <= '0;
    ##1;

    // Verify that hwif gets sampled at the same cycle as swacc strobe
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
                if(cb.hwif_out.r1.f.swacc) begin
                    latched_data = counter;
                    event_count++;
                end
            end
        end

        begin
            cpuif.read('h0, rd_data);
            repeat(4) @cb;
        end
    join_any
    disable fork;
    assert(rd_data == latched_data) else $error("Read returned 0x%0x but swacc strobed during 0x%0x", rd_data, latched_data);
    assert(event_count == 1) else $error("Observed excess swacc events: %0d", event_count);

    // Verify that writing a read-only register with no side effects never asserts swmod
    cb.hwif_in.r1.f.next <= 'h99;
    @cb;
    fork
        begin
            ##0;
            forever begin
                assert(cb.hwif_out.r1.f.swmod == 0);
                @cb;
            end
        end
        begin
            cpuif.write('h0, 'h0);
            cpuif.assert_read('h0, 'h99);
            repeat(4) @cb;
        end
    join_any
    disable fork;


    // Verify that hwif changes 1 cycle after swmod
    fired = 0;
    fork
        begin
            ##0;
            forever begin
                assert(cb.hwif_out.r2.f.value == 20);
                if(cb.hwif_out.r2.f.swmod) break;
                @cb;
            end
            fired = 1;
            @cb;
            forever begin
                assert(cb.hwif_out.r2.f.value == 21);
                assert(cb.hwif_out.r2.f.swmod == 0);
                @cb;
            end
        end

        begin
            cpuif.write('h1, 21);
            repeat(4) @cb;
        end
    join_any
    disable fork;
    assert(fired);

    // Verify that swmod does NOT trigger if strobes not set
    fired = 0;
    fork
        begin
            ##0;
            forever begin
                assert(cb.hwif_out.r2.f.value == 21);
                if(cb.hwif_out.r2.f.swmod) break;
                @cb;
            end
            fired = 1;
        end

        begin
            cpuif.write('h1, 22, 0);
            repeat(4) @cb;
        end
    join_any
    disable fork;
    assert(!fired);

    // Verify that hwif changes 1 cycle after swmod
    fired = 0;
    fork
        begin
            ##0;
            forever begin
                assert(cb.hwif_out.r3.f.value == 30);
                if(cb.hwif_out.r3.f.swmod) break;
                @cb;
            end
            fired = 1;
            @cb;
            forever begin
                assert(cb.hwif_out.r3.f.value == 0);
                assert(cb.hwif_out.r3.f.swmod == 0);
                @cb;
            end
        end

        begin
            cpuif.assert_read('h2, 30);
            repeat(4) @cb;
        end
    join_any
    disable fork;
    assert(fired);

    // Verify swacc and swmod assert when written
    fired = 0;
    fork
        begin
            ##0;
            forever begin
                assert(cb.hwif_out.r4.f.value == 'h12);
                if(cb.hwif_out.r4.f.swmod || cb.hwif_out.r4.f.swacc) begin
                    assert(cb.hwif_out.r4.f.swmod == 1);
                    assert(cb.hwif_out.r4.f.swacc == 1);
                    break;
                end
                @cb;
            end
            fired = 1;
            @cb;
            forever begin
                assert(cb.hwif_out.r4.f.value == 'h34);
                assert(cb.hwif_out.r4.f.swmod == 0);
                @cb;
            end
        end

        begin
            cpuif.write('h3, 'h34);
            repeat(4) @cb;
        end
    join_any
    disable fork;
    assert(fired);


    // Verify that hwif changes 1 cycle after swmod
    fired = 0;
    fork
        begin
            ##0;
            forever begin
                assert(cb.hwif_out.r5.f.value == 30);
                if(cb.hwif_out.r5.f.swmod) break;
                @cb;
            end
            fired = 1;
            @cb;
            forever begin
                assert(cb.hwif_out.r5.f.value == 0);
                assert(cb.hwif_out.r5.f.swmod == 0);
                @cb;
            end
        end

        begin
            cpuif.assert_read('h4, 30);
            repeat(4) @cb;
        end
    join_any
    disable fork;
    assert(fired);

{% endblock %}
