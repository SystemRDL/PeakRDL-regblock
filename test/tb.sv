module tb;
    timeunit 1ns;
    timeprecision 1ps;

    logic rst = '1;
    logic clk = '0;
    initial forever begin
        #10ns;
        clk = ~clk;
    end

    apb3_intf apb();

    apb3_intf_driver driver(
        .clk(clk),
        .m_apb(apb)
    );


    test_regblock dut (
        .clk(clk),
        .rst(rst),
        .s_apb(apb),
        .hwif_out()
    );


    initial begin
        logic [31:0] rd_data;

        repeat(5) @(posedge clk);
        rst = '0;
        repeat(5) @(posedge clk);

        driver.read('h000, rd_data);
        driver.write('h000, 'h0);
        driver.read('h000, rd_data);

        driver.read('h100, rd_data);
        driver.write('h100, 'h0);
        driver.read('h100, rd_data);

        driver.read('h000, rd_data);
        driver.write('h000, 'hFFFF_FFFF);
        driver.read('h000, rd_data);

        repeat(5) @(posedge clk);
        $finish();
    end

endmodule
