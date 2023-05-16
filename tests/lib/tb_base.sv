{% sv_line_anchor %}
module tb;
    timeunit 1ns;
    timeprecision 1ps;

    logic rst = '1;
    logic clk = '0;
    initial forever begin
        #5ns;
        clk = ~clk;
    end

    logic rst_n, arst, arst_n;
    assign rst_n = ~rst;
    assign arst = rst;
    assign arst_n = ~rst;

    //--------------------------------------------------------------------------
    // DUT Signal declarations
    //--------------------------------------------------------------------------
{%- if exporter.hwif.has_input_struct %}
    regblock_pkg::regblock__in_t hwif_in;
{%- endif %}

{%- if exporter.hwif.has_output_struct %}
    regblock_pkg::regblock__out_t hwif_out;
{%- endif %}

{%- if exporter.ds.has_paritycheck %}
    logic parity_error;
{%- endif %}


{%- block declarations %}
{%- endblock %}

    //--------------------------------------------------------------------------
    // Clocking
    //--------------------------------------------------------------------------
    default clocking cb @(posedge clk);
        default input #1step output #1;
        output rst;
{%- if exporter.hwif.has_input_struct and cls.clocking_hwif_in %}
        output hwif_in;
{%- endif %}

{%- if exporter.hwif.has_output_struct and cls.clocking_hwif_out %}
        input hwif_out;
{%- endif %}

{%- if exporter.ds.has_paritycheck %}
        input parity_error;
{%- endif %}

{%- filter indent %}
{%- block clocking_dirs %}
{%- endblock %}
{%- endfilter %}
    endclocking

    //--------------------------------------------------------------------------
    // CPUIF
    //--------------------------------------------------------------------------
    {{cls.cpuif.get_tb_inst(cls, exporter)|indent}}

    //--------------------------------------------------------------------------
    // DUT
    //--------------------------------------------------------------------------
    {% sv_line_anchor %}
    regblock dut (.*);

{%- if exporter.hwif.has_output_struct %}
    {% sv_line_anchor %}
    initial begin
        logic [$bits(hwif_out)-1:0] tmp;
        forever begin
            ##1;
            tmp = {>>{hwif_out}}; // Workaround for Xilinx's xsim - assign to tmp variable
            if(!rst) assert(!$isunknown(tmp)) else $error("hwif_out has X's!");
            {%- if exporter.ds.has_paritycheck %}
            if(!rst) assert(!$isunknown(parity_error)) else $error("parity_error has X's!");
            {%- endif %}
        end
    end
{%- endif %}
    {% sv_line_anchor %}

{%- block dut_support %}
{%- endblock %}

    //--------------------------------------------------------------------------
    // Test Sequence
    //--------------------------------------------------------------------------
    initial begin
        cb.rst <= '1;
    {%- if exporter.hwif.has_input_struct and cls.init_hwif_in %}
        cb.hwif_in <= '{default: '0};
    {%- endif %}

        begin
            {%- filter indent(8) %}
            {%- block seq %}
            {%- endblock %}
            {%- endfilter %}
        end
        {% sv_line_anchor %}
        ##5;
        $finish();
    end

    //--------------------------------------------------------------------------
    // Monitor for timeout
    //--------------------------------------------------------------------------
    initial begin
        ##{{cls.timeout_clk_cycles}};
        $fatal(1, "Test timed out after {{cls.timeout_clk_cycles}} clock cycles");
    end

endmodule
