library ieee;
context ieee.ieee_std_context;

package axi4lite_intf_pkg is

    type axi4lite_slave_in_intf is record
        AWVALID : std_logic;
        AWADDR : std_logic_vector;
        AWPROT : std_logic_vector(2 downto 0);

        WVALID : std_logic;
        WDATA : std_logic_vector;
        WSTRB : std_logic_vector;

        BREADY : std_logic;

        ARVALID : std_logic;
        ARADDR : std_logic_vector;
        ARPROT : std_logic_vector(2 downto 0);

        RREADY : std_logic;
    end record axi4lite_slave_in_intf;

    type axi4lite_slave_out_intf is record
        AWREADY : std_logic;

        WREADY : std_logic;

        BVALID : std_logic;
        BRESP : std_logic_vector(1 downto 0);

        ARREADY : std_logic;

        RVALID : std_logic;
        RDATA : std_logic_vector;
        RRESP : std_logic_vector(1 downto 0);
    end record axi4lite_slave_out_intf;

end package axi4lite_intf_pkg;

-- package body axi4lite_intf_pkg is
-- end package body axi4lite_intf_pkg;