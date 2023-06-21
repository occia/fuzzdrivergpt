#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>

#include "pjlib-util.h"
#include "pjlib.h"
#include "pjmedia-codec.h"
#include "pjmedia.h"
#include "pjmedia_audiodev.h"
#include "pjmedia_videodev.h"
#include "pjnath.h"
#include "pjsip.h"
#include "pjsip_simple.h"
#include "pjsip_ua.h"
#include "pjsua.h"

// ```
// // #include "pjlib-util.h"
// // #include "pjlib-util/xml.h"
// 
// //extern pj_xml_node * pj_xml_parse(pj_pool_t * pool,char * msg,pj_size_t len);
// 
// // the following function fuzzes pj_xml_parse
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//     // Allocate a memory pool factory for parsing xml message
//     pj_caching_pool cp;
//     pj_status_t status = pj_init();
//     if (status != PJ_SUCCESS) {
//         return 0;
//     }
//     pj_caching_pool_init(&cp, NULL, 4000);
//     pj_pool_t *pool = pj_pool_create(&cp.factory, NULL, 4000, 4000, NULL);
//     if (pool == NULL) {
//         pj_caching_pool_destroy(&cp);
//         pj_shutdown();
//         return 0;
//     }
// 
//     // Parse the xml message using pj_xml_parse function
//     pj_xml_node *node = pj_xml_parse(pool, (char*)Data, (pj_size_t)Size);
// 
//     // Cleanup memory pool
//     pj_pool_release(pool);
//     pj_caching_pool_destroy(&cp);
//     pj_shutdown();
// 
//     return 0;
// }
// ```
// 
// The above C code can be built successfully but will crash (ASAN-heap-buffer-overflow on address 0x6020000000f1 at pc 0x00000056ddd2 bp 0x7ffeffe05d40 sp 0x7ffeffe05d38).
// The crash line is:
// pj_xml_node *node = pj_xml_parse(pool, (char*)Data, (pj_size_t)Size);
// 
// The frames of the stack are:
// #0 0x56ddd1 in pj_scan_skip_whitespace /src/pjsip/pjlib-util/build/../src/pjlib-util/scanner.c:150:17
// #1 0x56d6a2 in pj_scan_init /src/pjsip/pjlib-util/build/../src/pjlib-util/scanner.c:130:9
// #2 0x56a223 in pj_xml_parse /src/pjsip/pjlib-util/build/../src/pjlib-util/xml.c:186:5
// #3 0x56a01c in LLVMFuzzerTestOneInput /root/workspace/jarvis/targets/pjsip/c/para-iter-account-10-0/dummyfuzzer.c:94:25
// 
// 
// 
// Based on the above information, fix the code.
// #include "pjlib-util.h"
// #include "pjlib-util/xml.h"

//extern pj_xml_node * pj_xml_parse(pj_pool_t * pool,char * msg,pj_size_t len);

// initialize PJLIB
static pj_status_t init_pjlib() {
    static pj_bool_t initialized = PJ_FALSE;
    pj_status_t status;

    if (!initialized) {
        status = pj_init();
        if (status != PJ_SUCCESS) {
            return status;
        }
        initialized = PJ_TRUE;
    }

    return PJ_SUCCESS;
}

// the following function fuzzes pj_xml_parse
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    // Allocate a memory pool factory for parsing xml message
    pj_caching_pool cp;
    pj_status_t status;
    pj_caching_pool_init(&cp, NULL, 4000);
    pj_pool_t *pool = pj_pool_create(&cp.factory, NULL, 4000, 4000, NULL);
    if (pool == NULL) {
        pj_caching_pool_destroy(&cp);
        return 0;
    }

    // Parse the xml message using pj_xml_parse function
    status = init_pjlib();
    if (status != PJ_SUCCESS) {
        pj_pool_release(pool);
        pj_caching_pool_destroy(&cp);
        return 0;
    }
    
    char* xml_data = (char*) pj_pool_alloc(pool, Size+1);
    pj_memcpy(xml_data, Data, Size);
    xml_data[Size] = '\0';

    pj_xml_node *node = pj_xml_parse(pool, xml_data, (pj_size_t)Size);

    // Cleanup memory pool
    pj_pool_release(pool);
    pj_caching_pool_destroy(&cp);

    return 0;
}