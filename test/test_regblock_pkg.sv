// TODO: Add a banner
package test_regblock_pkg;
    
    // test_regblock.r0.a
    typedef struct {
        logic [7:0] value;
        logic anded;
    } test_regblock__r0__a__out_t;

    // test_regblock.r0.b
    typedef struct {
        logic [7:0] value;
        logic ored;
    } test_regblock__r0__b__out_t;

    // test_regblock.r0.c
    typedef struct {
        logic [7:0] value;
        logic swmod;
    } test_regblock__r0__c__out_t;

    // test_regblock.r0
    typedef struct {
        test_regblock__r0__a__out_t a;
        test_regblock__r0__b__out_t b;
        test_regblock__r0__c__out_t c;
    } test_regblock__r0__out_t;

    // test_regblock.r1.a
    typedef struct {
        logic [7:0] value;
        logic anded;
    } test_regblock__r1__a__out_t;

    // test_regblock.r1.b
    typedef struct {
        logic [7:0] value;
        logic ored;
    } test_regblock__r1__b__out_t;

    // test_regblock.r1.c
    typedef struct {
        logic [7:0] value;
        logic swmod;
    } test_regblock__r1__c__out_t;

    // test_regblock.r1
    typedef struct {
        test_regblock__r1__a__out_t a;
        test_regblock__r1__b__out_t b;
        test_regblock__r1__c__out_t c;
    } test_regblock__r1__out_t;

    // test_regblock.r2.a
    typedef struct {
        logic [7:0] value;
        logic anded;
    } test_regblock__r2__a__out_t;

    // test_regblock.r2.b
    typedef struct {
        logic [7:0] value;
        logic ored;
    } test_regblock__r2__b__out_t;

    // test_regblock.r2.c
    typedef struct {
        logic [7:0] value;
        logic swmod;
    } test_regblock__r2__c__out_t;

    // test_regblock.r2
    typedef struct {
        test_regblock__r2__a__out_t a;
        test_regblock__r2__b__out_t b;
        test_regblock__r2__c__out_t c;
    } test_regblock__r2__out_t;

    // test_regblock
    typedef struct {
        test_regblock__r0__out_t r0;
        test_regblock__r1__out_t r1;
        test_regblock__r2__out_t r2;
    } test_regblock__out_t;
endpackage