// TODO: Add a banner
package test_regblock_pkg;
    
    // test_regblock.r2[].a
    typedef struct {
        logic [7:0] value;
        logic anded;
    } test_regblock__r2x__a__out_t;

    // test_regblock.r2[]
    typedef struct {
        test_regblock__r2x__a__out_t a;
    } test_regblock__r2x__out_t;

    // test_regblock
    typedef struct {
        test_regblock__r2x__out_t r2[112];
    } test_regblock__out_t;
endpackage