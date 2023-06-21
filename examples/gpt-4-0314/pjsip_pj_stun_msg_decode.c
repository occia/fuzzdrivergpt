#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

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
// // #include "pjnath/stun.h" // Add this line to include "pjnath/stun.h"
// // #include "pjnath/stun_msg.h"
// // #include "pjnath/stun_session.h"
// // #include "pjnath/errno.h"
// // #include "pjnath/stun_config.h"
// // #include "pjnath/constants.h"
// // #include "pjlib-util/types.h"
// // #include "pj/pool.h"
// // #include "pj/except.h"
// // #include "pj/os.h"
// // #include "pj/assert.h"
// // #include "pj/lock.h"
// // #include "pj/string.h"
// // #include "pj/log.h"
// // #include "pj/errno.h"
// // #include "pj/rand.h"
// // #include "pj/timer.h"
// // #include "pj/compat/socket.h"
// // #include "pj/compat/os.h"
// // #include "pj/ioqueue.h"
// // #include "pj/sock_select.h"
// // #include "pj/activesock.h"
// // #include "pj/addr_resolv.h"
// // #include "pj/sock_qos.h"
// // #include "pj/ssl_sock.h"
// 
// // Add this line to define PJ_STUN_MIN_PKT_LEN
// #define PJ_STUN_MIN_PKT_LEN 20
// 
// // The following function fuzzes pj_stun_msg_decode
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//     // Implement the fuzzing logic here
//     // You might need to call pj_stun_msg_decode() function with appropriate parameters
// 
//     return 0; // Return 0 as an example
// }
// ```
// 
// The above C code can be built successfully but its fuzzing seems not effective since the coverage never change.
// 
// Based on the above information, fix the code if necessary.
// #include "pjnath/stun.h"
// #include "pjnath/stun_msg.h"
// #include "pjnath/stun_session.h"
// #include "pjnath/errno.h"
// #include "pjnath/stun_config.h"
// #include "pjnath/constants.h"
// #include "pjlib-util/types.h"
// #include "pj/pool.h"
// #include "pj/except.h"
// #include "pj/os.h"
// #include "pj/assert.h"
// #include "pj/lock.h"
// #include "pj/string.h"
// #include "pj/log.h"
// #include "pj/errno.h"
// #include "pj/rand.h"
// #include "pj/timer.h"
// #include "pj/compat/socket.h"
// #include "pj/compat/os.h"
// #include "pj/ioqueue.h"
// #include "pj/sock_select.h"
// #include "pj/activesock.h"
// #include "pj/addr_resolv.h"
// #include "pj/sock_qos.h"
// #include "pj/ssl_sock.h"

#define PJ_STUN_MIN_PKT_LEN 20

static pj_pool_factory *g_pool_factory = NULL;

// Initializing pj_caching_pool and pj_pool_factory
static void init_pj_pool() {
    static pj_caching_pool caching_pool;

    pj_init();
    pj_caching_pool_init(&caching_pool, NULL, 0);
    g_pool_factory = &caching_pool.factory;
}

extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    if (!g_pool_factory) {
        init_pj_pool();
    }

    if (Size < PJ_STUN_MIN_PKT_LEN) {
        return 0;
    }

    pj_pool_t *pool = pj_pool_create(g_pool_factory, "fuzz_stun_pool", 512, 512, NULL);
    if (!pool) {
        return 0;
    }

    pj_stun_msg *stun_msg;
    pj_size_t parsed_len;
    pj_status_t status;

    // Call pj_stun_msg_decode() function with appropriate parameters
    status = pj_stun_msg_decode(pool, (const pj_uint8_t*)Data, (unsigned)Size, PJ_STUN_IS_DATAGRAM, &stun_msg, &parsed_len, NULL);

    // Clean up
    pj_pool_release(pool);

    return 0;
}