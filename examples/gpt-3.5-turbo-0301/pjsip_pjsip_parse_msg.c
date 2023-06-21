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
// // #include "pjsip.h"
// 
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//     // First, we need to initialize the PJSIP endpoint and create a pool
//     pj_status_t status;
//     pj_caching_pool cp; // change the type of pf to pj_caching_pool
//     pj_init();
//     pj_caching_pool_init(&cp, &pj_caching_pool_default_policy, 0); // use pj_caching_pool_default_policy instead of pj_pool_factory_default_policy
//     pj_pool_t* pool = pj_pool_create(&cp.factory, "fuzz_test", 4000, 4000, NULL);
//     pjsip_endpoint* endpt; // initialize the pjsip_endpoint pointer
// 
//     // Then, we need to create a buffer to store the input data
//     char* buf = (char*)malloc(Size + 1);
//     memcpy(buf, Data, Size);
//     buf[Size] = '\0';
// 
//     // Next, we need to initialize the error list and parse the message
//     pjsip_parser_err_report err_list;
//     pj_list_init(&err_list);
//     status = pjsip_endpt_create(&cp.factory, NULL, &endpt); // create the endpoint using cp.factory instead of pf
//     if (status != PJ_SUCCESS) {
//         pj_pool_release(pool);
//         return 1; // error handling
//     }
//     pjsip_msg* msg = pjsip_parse_msg(pool, buf, Size, &err_list);
// 
//     // Finally, we need to release the pool and free the buffer
//     pjsip_endpt_destroy(endpt); // destroy the endpoint
//     pj_pool_release(pool);
//     pj_caching_pool_destroy(&cp); // destroy the caching pool
//     free(buf);
// 
//     return 0;
// }
// ```
// 
// The above C code has compilation error.
// The error line is:
// pj_caching_pool_init(&cp, &pj_caching_pool_default_policy, 0); // use pj_caching_pool_default_policy instead of pj_pool_factory_default_policy
// 
// The error description is:
// use of undeclared identifier 'pj_caching_pool_default_policy'
// 
// The definition of `pj_caching_pool_init`:
// /**
//  * Initialize caching pool.
//  *
//  * @param ch_pool       The caching pool factory to be initialized.
//  * @param policy        Pool factory policy.
//  * @param max_capacity  The total capacity to be retained in the cache. When
//  *                      the pool is returned to the cache, it will be kept in
//  *                      recycling list if the total capacity of pools in this
//  *                      list plus the capacity of the pool is still below this
//  *                      value.
//  */
// extern void pj_caching_pool_init(pj_caching_pool * ch_pool,const pj_pool_factory_policy * policy,pj_size_t max_capacity);
// 
// // @ examples of API `pj_caching_pool_init` usage from /tmp/sourcegraph_tmpdir/github.com/elastos/Elastos/Carrier/src/session/ice.c
// // static
// // int ice_worker_init(IceWorker *worker, IceTransportOptions *opts)
// // {
// //     char name[128] = {0};
// //     pj_status_t status;
// // 
// //     /* Must create pool factory, where memory allocations come from */
// //     pj_caching_pool_init(&worker->cp, NULL, 0);
// // 
// //     /* Init our ICE settings with null values */
// //     pj_ice_strans_cfg_default(&worker->cfg);
// // 
// //     worker->cfg.stun_cfg.pf = &worker->cp.factory;
// // 
// //     sprintf(name, "ice-worker-%d", worker->base.id);
// // 
// //     worker->pool = pj_pool_create(&worker->cp.factory, name, 1024, 512, NULL);
// //     if (!worker->pool) {
// //         vlogE("Session: ICE worker %d create memory pool failed.", worker->base.id);
// //         return ELA_GENERAL_ERROR(ELAERR_OUT_OF_MEMORY);
// //     }
// // 
// //     if (opts->stun_host)
// //         pj_strdup2_with_null(worker->pool, &worker->stun_server, opts->stun_host);
// // 
// //     if (opts->stun_port)
// //         worker->stun_port = atoi(opts->stun_port);
// //     else
// //         worker->stun_port = PJ_STUN_PORT;
// // 
// //     if (opts->turn_host)
// //         pj_strdup2_with_null(worker->pool, &worker->turn_server, opts->turn_host);
// // 
// //     if (opts->turn_port)
// //         worker->turn_port = atoi(opts->turn_port);
// //     else
// //         worker->turn_port = PJ_STUN_PORT;
// // 
// //     if (opts->turn_username)
// //         pj_strdup2_with_null(worker->pool, &worker->turn_username, opts->turn_username);
// // 
// //     if (opts->turn_password)
// //         pj_strdup2_with_null(worker->pool, &worker->turn_password, opts->turn_password);
// // 
// //     if (opts->turn_realm)
// //         pj_strdup2_with_null(worker->pool, &worker->turn_realm, opts->turn_realm);
// // 
// //     /* Create timer heap for timer stuff */
// //     status = pj_timer_heap_create(worker->pool, 100, &worker->cfg.stun_cfg.timer_heap);
// //     if (status != PJ_SUCCESS) {
// //         vlogE("Session: ICE worker %d create timer heap failed: %s",
// //               worker->base.id, ice_strerror(status));
// //         return ELA_ICE_ERROR(status);
// //     }
// // 
// //     /* and create ioqueue for network I/O stuff */
// //     status = pj_ioqueue_create(worker->pool, 64, &worker->cfg.stun_cfg.ioqueue);
// //     if (status != PJ_SUCCESS) {
// //         vlogE("Session: ICE worker %d create I/O queue failed: %s",
// //               worker->base.id, ice_strerror(status));
// //         return ELA_ICE_ERROR(status);
// //     }
// // 
// //     worker->cfg.af = pj_AF_INET();
// //     worker->regular = PJ_TRUE;
// // 
// //     /* -= Start initializing ICE stream transport config =- */
// // 
// //     /* Maximum number of host candidates */
// //     worker->cfg.stun.max_host_cands = PJ_ICE_ST_MAX_CAND;
// // 
// //     /* Nomination strategy */
// //     worker->cfg.opt.aggressive = !worker->regular;
// // 
// //     /* Configure STUN/srflx & TURN candidate resolution */
// //     if (worker->stun_server.slen) {
// //         worker->cfg.stun_tp_cnt = 1;
// //         pj_ice_strans_stun_cfg_default(&worker->cfg.stun_tp[0]);
// //         worker->cfg.stun_tp[0].af = pj_AF_INET();
// //         worker->cfg.stun_tp[0].server = worker->stun_server;
// //         worker->cfg.stun_tp[0].port = worker->stun_port;
// //     }
// // 
// //     if (worker->turn_server.slen) {
// //         worker->cfg.turn_tp_cnt = 1;
// //         pj_ice_strans_turn_cfg_default(&worker->cfg.turn_tp[0]);
// //         worker->cfg.turn_tp[0].af = pj_AF_INET();
// //         worker->cfg.turn_tp[0].server = worker->turn_server;
// //         worker->cfg.turn_tp[0].port = worker->turn_port;
// // 
// //         /* For this demo app, configure longer STUN keep-alive time
// //          * so that it does't clutter the screen output.
// //          */
// //         worker->cfg.stun_tp[0].cfg.ka_interval = KA_INTERVAL;
// //         worker->cfg.stun_tp[0].cfg.ka_interval = KA_INTERVAL;
// //         worker->cfg.turn_tp[0].alloc_param.ka_interval = KA_INTERVAL;
// // 
// //         worker->cfg.turn_tp[0].auth_cred.type = PJ_STUN_AUTH_CRED_STATIC;
// //         worker->cfg.turn_tp[0].auth_cred.data.static_cred.realm = worker->turn_realm;
// //         worker->cfg.turn_tp[0].auth_cred.data.static_cred.username = worker->turn_username;
// //         worker->cfg.turn_tp[0].auth_cred.data.static_cred.data_type = PJ_STUN_PASSWD_PLAIN;
// //         worker->cfg.turn_tp[0].auth_cred.data.static_cred.data = worker->turn_password;
// // 
// //         worker->cfg.turn_tp[0].conn_type = PJ_TURN_TP_UDP;
// //     }
// // 
// //     // The read_key and write_key are used for reporting state changed.
// //     status = ice_register_event(worker, &worker->read_key, &worker->read_addr);
// //     if (status != PJ_SUCCESS) {
// //         vlogE("Session: ICE worker %d register read event failed: %s",
// //               worker->base.id, ice_strerror(status));
// //         return ELA_ICE_ERROR(status);
// //     }
// // 
// //     status = ice_register_event(worker, &worker->write_key, NULL);
// //     if (status != 0) {
// //         vlogE("Session: ICE worker %d register write event failed: %s",
// //               worker->base.id, ice_strerror(status));
// //         return ELA_ICE_ERROR(status);
// //     }
// // 
// //     vlogD("Session: ICE worker %d initialized.", worker->base.id);
// // 
// //     return 0;
// // }
// 
// 
// Based on the above information, fix the code.
// #include "pjsip.h"

extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    // First, we need to initialize the PJSIP endpoint and create a pool
    pj_status_t status;
    pj_caching_pool cp; // change the type of pf to pj_caching_pool
    pj_init();
    pj_caching_pool_init(&cp, &pj_pool_factory_default_policy, 0); // use pj_pool_factory_default_policy instead of pj_caching_pool_default_policy
    pj_pool_t* pool = pj_pool_create(&cp.factory, "fuzz_test", 4000, 4000, NULL);
    pjsip_endpoint* endpt; // initialize the pjsip_endpoint pointer

    // Then, we need to create a buffer to store the input data
    char* buf = (char*)malloc(Size + 1);
    memcpy(buf, Data, Size);
    buf[Size] = '\0';

    // Next, we need to initialize the error list and parse the message
    pjsip_parser_err_report err_list;
    pj_list_init(&err_list);
    status = pjsip_endpt_create(&cp.factory, NULL, &endpt); // create the endpoint using cp.factory instead of pf
    if (status != PJ_SUCCESS) {
        pj_pool_release(pool);
        return 1; // error handling
    }
    pjsip_msg* msg = pjsip_parse_msg(pool, buf, Size, &err_list);

    // Finally, we need to release the pool and free the buffer
    pjsip_endpt_destroy(endpt); // destroy the endpoint
    pj_pool_release(pool);
    pj_caching_pool_destroy(&cp); // destroy the caching pool
    free(buf);

    return 0;
}