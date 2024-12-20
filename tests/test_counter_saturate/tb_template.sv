{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // counter controls are the same for each sub-test
    `define incr (1<<9)
    `define decr (1<<10)
    `define clr (1<<11)
    `define set (1<<12)
    `define step(n) (n<<16)

    //--------------------------------------------------------------------------
    // Test incrsaturate = true; decrsaturate = true;
    //--------------------------------------------------------------------------
    cpuif.assert_read('h0, 'h00, 'hFF);

    // incrsaturate via +1
    cpuif.write('h0, `set);
    cpuif.assert_read('h0, 'hFF, 'hFF);
    cpuif.write('h0, `decr + `step(1));
    cpuif.assert_read('h0, 'hFE, 'hFF);
    cpuif.write('h0, `incr + `step(1));
    cpuif.assert_read('h0, 'hFF, 'hFF);
    cpuif.write('h0, `incr + `step(1));
    cpuif.assert_read('h0, 'hFF, 'hFF);

    // decrsaturate via +1
    cpuif.write('h0, `clr);
    cpuif.assert_read('h0, 'h00, 'hFF);
    cpuif.write('h0, `incr + `step(1));
    cpuif.assert_read('h0, 'h01, 'hFF);
    cpuif.write('h0, `decr + `step(1));
    cpuif.assert_read('h0, 'h00, 'hFF);
    cpuif.write('h0, `decr + `step(1));
    cpuif.assert_read('h0, 'h00, 'hFF);

    // incrsaturate via larger steps
    cpuif.write('h0, `set);
    cpuif.assert_read('h0, 'hFF, 'hFF);
    cpuif.write('h0, `decr + `step(1));
    cpuif.assert_read('h0, 'hFE, 'hFF);
    cpuif.write('h0, `incr + `step(2));
    cpuif.assert_read('h0, 'hFF, 'hFF);
    cpuif.write('h0, `incr + `step(3));
    cpuif.assert_read('h0, 'hFF, 'hFF);
    cpuif.write('h0, `incr + `step(255));
    cpuif.assert_read('h0, 'hFF, 'hFF);

    // decrsaturate via larger steps
    cpuif.write('h0, `clr);
    cpuif.assert_read('h0, 'h00, 'hFF);
    cpuif.write('h0, `incr + `step(1));
    cpuif.assert_read('h0, 'h01, 'hFF);
    cpuif.write('h0, `decr + `step(2));
    cpuif.assert_read('h0, 'h00, 'hFF);
    cpuif.write('h0, `decr + `step(3));
    cpuif.assert_read('h0, 'h00, 'hFF);
    cpuif.write('h0, `decr + `step(255));
    cpuif.assert_read('h0, 'h00, 'hFF);

    //--------------------------------------------------------------------------
    // Test incrsaturate = 250; decrsaturate = 5;
    //--------------------------------------------------------------------------
    cpuif.assert_read('h4, 'h00, 'hFF);

    // incrsaturate via +1
    cpuif.write('h4, `set);
    cpuif.assert_read('h4, 'hFF, 'hFF);
    cpuif.write('h4, `decr + `step(1));
    cpuif.assert_read('h4, 'hFE, 'hFF);
    cpuif.write('h4, `incr + `step(1));
    cpuif.assert_read('h4, 'hFA, 'hFF);
    cpuif.write('h4, `incr + `step(1));
    cpuif.assert_read('h4, 'hFA, 'hFF);

    // decrsaturate via +1
    cpuif.write('h4, `clr);
    cpuif.assert_read('h4, 'h00, 'hFF);
    cpuif.write('h4, `incr + `step(1));
    cpuif.assert_read('h4, 'h01, 'hFF);
    cpuif.write('h4, `decr + `step(1));
    cpuif.assert_read('h4, 'h05, 'hFF);
    cpuif.write('h4, `decr + `step(1));
    cpuif.assert_read('h4, 'h05, 'hFF);

    // incrsaturate via larger steps
    cpuif.write('h4, `set);
    cpuif.assert_read('h4, 'hFF, 'hFF);
    cpuif.write('h4, `decr + `step(1));
    cpuif.assert_read('h4, 'hFE, 'hFF);
    cpuif.write('h4, `incr + `step(2));
    cpuif.assert_read('h4, 'hFA, 'hFF);
    cpuif.write('h4, `incr + `step(3));
    cpuif.assert_read('h4, 'hFA, 'hFF);
    cpuif.write('h4, `incr + `step(255));
    cpuif.assert_read('h4, 'hFA, 'hFF);

    // decrsaturate via larger steps
    cpuif.write('h4, `clr);
    cpuif.assert_read('h4, 'h00, 'hFF);
    cpuif.write('h4, `incr + `step(1));
    cpuif.assert_read('h4, 'h01, 'hFF);
    cpuif.write('h4, `decr + `step(2));
    cpuif.assert_read('h4, 'h05, 'hFF);
    cpuif.write('h4, `decr + `step(3));
    cpuif.assert_read('h4, 'h05, 'hFF);
    cpuif.write('h4, `decr + `step(255));
    cpuif.assert_read('h4, 'h05, 'hFF);

    //--------------------------------------------------------------------------
    // Test incrsaturate = <ref 255>; decrsaturate = <ref 0>;
    //--------------------------------------------------------------------------
    cpuif.assert_read('h8, 'h00, 'hFF);

    // incrsaturate via +1
    cpuif.write('h8, `set);
    cpuif.assert_read('h8, 'hFF, 'hFF);
    cpuif.write('h8, `decr + `step(1));
    cpuif.assert_read('h8, 'hFE, 'hFF);
    cpuif.write('h8, `incr + `step(1));
    cpuif.assert_read('h8, 'hFF, 'hFF);
    cpuif.write('h8, `incr + `step(1));
    cpuif.assert_read('h8, 'hFF, 'hFF);

    // decrsaturate via +1
    cpuif.write('h8, `clr);
    cpuif.assert_read('h8, 'h00, 'hFF);
    cpuif.write('h8, `incr + `step(1));
    cpuif.assert_read('h8, 'h01, 'hFF);
    cpuif.write('h8, `decr + `step(1));
    cpuif.assert_read('h8, 'h00, 'hFF);
    cpuif.write('h8, `decr + `step(1));
    cpuif.assert_read('h8, 'h00, 'hFF);

    // incrsaturate via larger steps
    cpuif.write('h8, `set);
    cpuif.assert_read('h8, 'hFF, 'hFF);
    cpuif.write('h8, `decr + `step(1));
    cpuif.assert_read('h8, 'hFE, 'hFF);
    cpuif.write('h8, `incr + `step(2));
    cpuif.assert_read('h8, 'hFF, 'hFF);
    cpuif.write('h8, `incr + `step(3));
    cpuif.assert_read('h8, 'hFF, 'hFF);
    cpuif.write('h8, `incr + `step(255));
    cpuif.assert_read('h8, 'hFF, 'hFF);

    // decrsaturate via larger steps
    cpuif.write('h8, `clr);
    cpuif.assert_read('h8, 'h00, 'hFF);
    cpuif.write('h8, `incr + `step(1));
    cpuif.assert_read('h8, 'h01, 'hFF);
    cpuif.write('h8, `decr + `step(2));
    cpuif.assert_read('h8, 'h00, 'hFF);
    cpuif.write('h8, `decr + `step(3));
    cpuif.assert_read('h8, 'h00, 'hFF);
    cpuif.write('h8, `decr + `step(255));
    cpuif.assert_read('h8, 'h00, 'hFF);

    //--------------------------------------------------------------------------
    // Test incrsaturate = <ref 250>; decrsaturate = <ref 5>;
    //--------------------------------------------------------------------------
    cpuif.write('hc, 'hFA_05);

    cpuif.assert_read('h4, 'h05, 'hFF);

    // incrsaturate via +1
    cpuif.write('h8, `set);
    cpuif.assert_read('h8, 'hFF, 'hFF);
    cpuif.write('h8, `decr + `step(1));
    cpuif.assert_read('h8, 'hFE, 'hFF);
    cpuif.write('h8, `incr + `step(1));
    cpuif.assert_read('h8, 'hFA, 'hFF);
    cpuif.write('h8, `incr + `step(1));
    cpuif.assert_read('h8, 'hFA, 'hFF);

    // decrsaturate via +1
    cpuif.write('h8, `clr);
    cpuif.assert_read('h8, 'h00, 'hFF);
    cpuif.write('h8, `incr + `step(1));
    cpuif.assert_read('h8, 'h01, 'hFF);
    cpuif.write('h8, `decr + `step(1));
    cpuif.assert_read('h8, 'h05, 'hFF);
    cpuif.write('h8, `decr + `step(1));
    cpuif.assert_read('h8, 'h05, 'hFF);

    // incrsaturate via larger steps
    cpuif.write('h8, `set);
    cpuif.assert_read('h8, 'hFF, 'hFF);
    cpuif.write('h8, `decr + `step(1));
    cpuif.assert_read('h8, 'hFE, 'hFF);
    cpuif.write('h8, `incr + `step(2));
    cpuif.assert_read('h8, 'hFA, 'hFF);
    cpuif.write('h8, `incr + `step(3));
    cpuif.assert_read('h8, 'hFA, 'hFF);
    cpuif.write('h8, `incr + `step(255));
    cpuif.assert_read('h8, 'hFA, 'hFF);

    // decrsaturate via larger steps
    cpuif.write('h8, `clr);
    cpuif.assert_read('h8, 'h00, 'hFF);
    cpuif.write('h8, `incr + `step(1));
    cpuif.assert_read('h8, 'h01, 'hFF);
    cpuif.write('h8, `decr + `step(2));
    cpuif.assert_read('h8, 'h05, 'hFF);
    cpuif.write('h8, `decr + `step(3));
    cpuif.assert_read('h8, 'h05, 'hFF);
    cpuif.write('h8, `decr + `step(255));
    cpuif.assert_read('h8, 'h05, 'hFF);

{% endblock %}
