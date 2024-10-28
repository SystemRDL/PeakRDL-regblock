library ieee;
context ieee.ieee_std_context;

package apb4_intf_pkg is

    type apb4_slave_in_intf is record
        PSEL : std_logic;
        PENABLE : std_logic;
        PWRITE : std_logic;
        PPROT : std_logic_vector(2 downto 0);
        PADDR : std_logic_vector;
        PWDATA : std_logic_vector;
        PSTRB : std_logic_vector;
    end record apb4_slave_in_intf;

    type apb4_slave_out_intf is record
        PRDATA : std_logic_vector;
        PREADY : std_logic;
        PSLVERR : std_logic;
    end record apb4_slave_out_intf;

end package apb4_intf_pkg;

-- package body apb4_intf_pkg is
-- end package body apb4_intf_pkg;
