{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    int event_count;

    ##1;
    cb.rst <= '0;
    ##1;

    // No pulse if writing zero
    event_count = 0;
    fork
        begin
            ##0;
            forever begin
                @cb;
                if(cb.hwif_out.r1.f.value) begin
                    event_count++;
                end
            end
        end

        begin
            cpuif.write('h0, 'h0);
            repeat(5) @cb;
        end
    join_any
    disable fork;
    assert(event_count == 0) else $error("Observed excess singlepulse events: %0d", event_count);

    // single pulse
    event_count = 0;
    fork
        begin
            ##0;
            forever begin
                @cb;
                if(cb.hwif_out.r1.f.value) begin
                    event_count++;
                end
            end
        end

        begin
            cpuif.write('h0, 'h1);
            repeat(5) @cb;
        end
    join_any
    disable fork;
    assert(event_count == 1) else $error("Observed incorrect number of singlepulse events: %0d", event_count);

    // auto-clears
    cpuif.assert_read('h0, 'h0);

{% endblock %}
