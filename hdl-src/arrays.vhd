library ieee;
context ieee.ieee_std_context;

package arrays is

  type std_logic_array1 is array(natural range<>) of std_logic;
  type std_logic_array2 is array(natural range<>, natural range<>) of std_logic;
  type std_logic_array3 is array(natural range<>, natural range<>, natural range<>) of std_logic;
  type std_logic_array4 is array(natural range<>, natural range<>, natural range<>, natural range<>) of std_logic;
  type std_logic_array5 is array(natural range<>, natural range<>, natural range<>, natural range<>, natural range<>) of std_logic;

  type std_logic_vector_array1 is array(natural range<>) of std_logic_vector;
  type std_logic_vector_array2 is array(natural range<>, natural range<>) of std_logic_vector;
  type std_logic_vector_array3 is array(natural range<>, natural range<>, natural range<>) of std_logic_vector;
  type std_logic_vector_array4 is array(natural range<>, natural range<>, natural range<>, natural range<>) of std_logic_vector;
  type std_logic_vector_array5 is array(natural range<>, natural range<>, natural range<>, natural range<>, natural range<>) of std_logic_vector;

end package arrays;