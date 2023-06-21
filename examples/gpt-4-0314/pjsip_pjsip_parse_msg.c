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
// //#include "pjsip/sip_parser.h"
// 
// // @ examples of API usage from pjproject-2.0-device/pjsip/src/test/msg_err_test.c-msg_err_test
// // int msg_err_test(void)
// // {
// //     pj_pool_t *pool;
// //     unsigned i;
// // 
// //     PJ_LOG(3,(THIS_FILE, "Testing parsing error"));
// // 
// //     pool = pjsip_endpt_create_pool(endpt, "msgerrtest", 4000, 4000);
// // 
// //     for (i=0; i<PJ_ARRAY_SIZE(test_entries); ++i) {
// // 	pjsip_parser_err_report err_list, *e;
// // 	pjsip_msg *msg;
// // 
// // 	PJ_LOG(3,(THIS_FILE, "  Parsing msg %d", i));
// // 	pj_list_init(&err_list);
// // 	msg = pjsip_parse_msg(pool, test_entries[i].msg,
// // 			      strlen(test_entries[i].msg), &err_list);
// // 
// // 	e = err_list.next;
// // 	while (e != &err_list) {
// // 	    PJ_LOG(3,(THIS_FILE, 
// // 		      "   reported syntax error at line %d col %d for %.*s",
// // 		      e->line, e->col,
// // 		      (int)e->hname.slen,
// // 		      e->hname.ptr));
// // 	    e = e->next;
// // 	}
// //     }
// // 
// //     pj_pool_release(pool);
// //     return 0;
// // }
// 
// //extern pjsip_msg * pjsip_parse_msg(pj_pool_t * pool,char * buf,pj_size_t size,pjsip_parser_err_report * err_list);
// //extern pj_pool_t * pjsip_endpt_create_pool(pjsip_endpoint * endpt,const char * pool_name,pj_size_t initial,pj_size_t increment);
// //extern void pj_list_init(pj_list_type * node);
// //extern void pj_pool_release(pj_pool_t * pool);
// 
// // the following function fuzzes pjsip_parse_msg based on the above API usages
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
// if (Size == 0 || Data == NULL) {
//         return 0;
//     }
// 
//     // Initialize pjsip endpoint
//     pjsip_endpoint *endpt;
//     pj_status_t status = pjsip_endpt_create(&endpt);
//     if (status != PJ_SUCCESS) {
//         return 0;
//     }
// 
//     // Create a memory pool
//     pj_pool_t *pool = pjsip_endpt_create_pool(endpt, "fuzz_pool", 4096, 4096);
//     if (pool == NULL) {
//         pjsip_endpt_destroy(endpt);
//         return 0;
//     }
// 
//     // Create a buffer and copy the input data
//     char *buf = (char *)pj_pool_alloc(pool, Size + 1);
//     memcpy(buf, Data, Size);
//     buf[Size] = '\0';
// 
//     // Initialize error list
//     pjsip_parser_err_report err_list;
//     pj_list_init(&err_list);
// 
//     // Call the target function
//     pjsip_msg *msg = pjsip_parse_msg(pool, buf, Size, &err_list);
// 
//     // Release resources
//     pj_pool_release(pool);
//     pjsip_endpt_destroy(endpt);
// 
//     return 0;
// }
// ```
// 
// The above C code has compilation error.
// The error line is:
// pj_status_t status = pjsip_endpt_create(&endpt);
// 
// The error description is:
// too few arguments to function call, expected 3, have 1
// 
// The definition of `pjsip_endpt_create`:
// /**
//  * Create an instance of SIP endpoint from the specified pool factory.
//  * The pool factory reference then will be kept by the endpoint, so that 
//  * future memory allocations by SIP components will be taken from the same
//  * pool factory.
//  *
//  * @param pf            Pool factory that will be used for the lifetime of 
//  *                      endpoint.
//  * @param name          Optional name to be specified for the endpoint.
//  *                      If this parameter is NULL, then the name will use
//  *                      local host name.
//  * @param endpt         Pointer to receive endpoint instance.
//  *
//  * @return              PJ_SUCCESS on success.
//  */
// extern pj_status_t pjsip_endpt_create(pj_pool_factory * pf,const char * name,pjsip_endpoint ** endpt);
// 
// // @ examples of API `pjsip_endpt_create` usage from /tmp/sourcegraph_tmpdir/github.com/jchavanton/voip_perf/src/voip_perf.c
// // static pj_status_t create_app(void) {
// // 	pj_status_t status;
// // 
// // 	status = pj_init();
// // 	if (status != PJ_SUCCESS) {
// // 		app_perror(THIS_FILE, "Error initializing pjlib", status);
// // 		return status;
// // 	}
// // 
// // 	/* init settings */
// // 	app.client_mode = PJ_FALSE;
// // 
// // 	/* init PJLIB-UTIL: */
// // 	status = pjlib_util_init();
// // 	PJ_ASSERT_RETURN(status == PJ_SUCCESS, status);
// // 
// // 	/* Must create a pool factory before we can allocate any memory. */
// // 	pj_caching_pool_init(&app.cp, &pj_pool_factory_default_policy, CACHING_POOL_SIZE);
// // 
// // 	/* Create application pool for misc. */
// // 	app.pool = pj_pool_create(&app.cp.factory, "app", 1000, 1000, NULL);
// // 
// // 	/* Create the endpoint: */
// // 	status = pjsip_endpt_create(&app.cp.factory, pj_gethostname()->ptr, &app.sip_endpt);
// // 	PJ_ASSERT_RETURN(status == PJ_SUCCESS, status);
// // 
// // 	return status;
// // }
// 
// 
// Based on the above information, fix the code.
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    if (Size == 0 || Data == NULL) {
        return 0;
    }

    // Initialize PJLIB
    pj_status_t pj_status = pj_init();
    if (pj_status != PJ_SUCCESS) {
        return 0;
    }

    // Create a caching pool
    pj_caching_pool caching_pool;
    pj_caching_pool_init(&caching_pool, &pj_pool_factory_default_policy, 0);

    // Initialize pjsip endpoint
    pjsip_endpoint *endpt;
    pj_status_t status = pjsip_endpt_create(&caching_pool.factory, pj_gethostname()->ptr, &endpt);
    if (status != PJ_SUCCESS) {
        pj_caching_pool_destroy(&caching_pool);
        return 0;
    }

    // Create a memory pool
    pj_pool_t *pool = pjsip_endpt_create_pool(endpt, "fuzz_pool", 4096, 4096);
    if (pool == NULL) {
        pjsip_endpt_destroy(endpt);
        pj_caching_pool_destroy(&caching_pool);
        return 0;
    }

    // Create a buffer and copy the input data
    char *buf = (char *)pj_pool_alloc(pool, Size + 1);
    memcpy(buf, Data, Size);
    buf[Size] = '\0';

    // Initialize error list
    pjsip_parser_err_report err_list;
    pj_list_init(&err_list);

    // Call the target function
    pjsip_msg *msg = pjsip_parse_msg(pool, buf, Size, &err_list);

    // Release resources
    pj_pool_release(pool);
    pjsip_endpt_destroy(endpt);
    pj_caching_pool_destroy(&caching_pool);

    return 0;
}