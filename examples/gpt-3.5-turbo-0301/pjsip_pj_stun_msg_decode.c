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
// // #include "pjlib-util/pjlib-util.h"
// 
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//     pj_caching_pool cp;
//     pj_pool_t *pool;
//     pj_stun_msg *msg;
// 
//     pj_caching_pool_init(&cp, NULL, 0);
//     pool = pj_pool_create(&cp.factory, "pool", 512, 512, NULL);
//     pj_status_t status = pj_stun_msg_decode(pool, Data, Size, PJ_STUN_IS_DATAGRAM | PJ_STUN_CHECK_PACKET, &msg, NULL, NULL);
//     pj_pool_release(pool);
//     pj_caching_pool_destroy(&cp);
// 
//     return 0;
// }
// ```
// 
// The above C code can be built successfully but will crash (libFuzzer-deadly signal).
// The crash line is:
// pj_status_t status = pj_stun_msg_decode(pool, Data, Size, PJ_STUN_IS_DATAGRAM | PJ_STUN_CHECK_PACKET, &msg, NULL, NULL);
// 
// The frames of the stack are:
// #0 0x5391f1 in __sanitizer_print_stack_trace /src/llvm-project/compiler-rt/lib/asan/asan_stack.cpp:87:3
// #1 0x457d08 in fuzzer::PrintStackTrace() /src/llvm-project/compiler-rt/lib/fuzzer/FuzzerUtil.cpp:210:5
// #2 0x43c9e3 in fuzzer::Fuzzer::CrashCallback() /src/llvm-project/compiler-rt/lib/fuzzer/FuzzerLoop.cpp:233:3
// #3 0x7fcef3a0341f  (/lib/x86_64-linux-gnu/libpthread.so.0+0x1441f) (BuildId: 7b4536f41cdaa5888408e82d0836e33dcf436466)
// #4 0x7fcef381d00a in raise (/lib/x86_64-linux-gnu/libc.so.6+0x4300a) (BuildId: 1878e6b475720c7c51969e69ab2d276fae6d1dee)
// #5 0x7fcef37fc858 in abort (/lib/x86_64-linux-gnu/libc.so.6+0x22858) (BuildId: 1878e6b475720c7c51969e69ab2d276fae6d1dee)
// #6 0x7fcef37fc728  (/lib/x86_64-linux-gnu/libc.so.6+0x22728) (BuildId: 1878e6b475720c7c51969e69ab2d276fae6d1dee)
// #7 0x7fcef380dfd5 in __assert_fail (/lib/x86_64-linux-gnu/libc.so.6+0x33fd5) (BuildId: 1878e6b475720c7c51969e69ab2d276fae6d1dee)
// #8 0x570df3 in pj_stun_msg_decode /src/pjsip/pjnath/build/../src/pjnath/stun_msg.c:2318:5
// #9 0x56a03c in LLVMFuzzerTestOneInput /root/workspace/jarvis/targets/pjsip/c/para-iter-account-8-0/dummyfuzzer.c:101:26
// 
// The frame `pj_stun_msg_decode` related code:
// 2317	
// 2318	PJ_ASSERT_RETURN(pool && pdu && pdu_len && p_msg, PJ_EINVAL);
// 2319	PJ_ASSERT_RETURN(sizeof(pj_stun_msg_hdr) == 20, PJ_EBUG);
// 
// The definition of `pj_stun_msg_decode`:
// /**
//  * Decode incoming packet into STUN message.
//  *
//  * @param pool          Pool to allocate the message.
//  * @param pdu           The incoming packet to be parsed.
//  * @param pdu_len       The length of the incoming packet.
//  * @param options       Parsing flags, according to pj_stun_decode_options.
//  * @param p_msg         Pointer to receive the parsed message.
//  * @param p_parsed_len  Optional pointer to receive how many bytes have
//  *                      been parsed for the STUN message. This is useful
//  *                      when the packet is received over stream oriented
//  *                      transport.
//  * @param p_response    Optional pointer to receive an instance of response
//  *                      message, if one can be created. If the packet being
//  *                      decoded is a request message, and it contains error,
//  *                      and a response can be created, then the STUN 
//  *                      response message will be returned on this argument.
//  *
//  * @return              PJ_SUCCESS if a STUN message has been successfully
//  *                      decoded.
//  */
// extern pj_status_t pj_stun_msg_decode(pj_pool_t * pool,const pj_uint8_t * pdu,pj_size_t pdu_len,unsigned int options,pj_stun_msg ** p_msg,pj_size_t * p_parsed_len,pj_stun_msg ** p_response);
// 
// // @ examples of API `pj_stun_msg_decode` usage from /tmp/sourcegraph_tmpdir/github.com/radif/SIPHON-SIP-Client-that-actually-compiles/pjproject-2.0-device/pjnath/src/pjnath-test/stun.c
// // static int decode_test(void)
// // {
// //     unsigned i;
// //     pj_pool_t *pool;
// //     int rc = 0;
// //     
// //     pool = pj_pool_create(mem, "decode_test", 1024, 1024, NULL);
// // 
// //     PJ_LOG(3,(THIS_FILE, "  STUN decode test"));
// // 
// //     for (i=0; i<PJ_ARRAY_SIZE(tests); ++i) {
// // 	struct test *t = &tests[i];
// // 	pj_stun_msg *msg, *msg2;
// // 	pj_uint8_t buf[1500];
// // 	pj_str_t key;
// // 	pj_size_t len;
// // 	pj_status_t status;
// // 
// // 	PJ_LOG(3,(THIS_FILE, "   %s", t->title));
// // 
// // 	if (t->pdu) {
// // 	    status = pj_stun_msg_decode(pool, (pj_uint8_t*)t->pdu, t->pdu_len,
// // 				        PJ_STUN_IS_DATAGRAM | PJ_STUN_CHECK_PACKET, 
// // 					&msg, NULL, NULL);
// // 
// // 	    /* Check expected decode result */
// // 	    if (t->expected_status != status) {
// // 		PJ_LOG(1,(THIS_FILE, "    expecting status %d, got %d",
// // 		          t->expected_status, status));
// // 		rc = -10;
// // 		goto on_return;
// // 	    }
// // 
// // 	} else {
// // 	    msg = t->create(pool);
// // 	    status = PJ_SUCCESS;
// // 	}
// // 
// // 	if (status != PJ_SUCCESS)
// // 	    continue;
// // 
// // 	/* Try to encode message */
// // 	pj_stun_create_key(pool, &key, NULL, &USERNAME, PJ_STUN_PASSWD_PLAIN, &PASSWORD);
// // 	status = pj_stun_msg_encode(msg, buf, sizeof(buf), 0, &key, &len);
// // 	if (status != PJ_SUCCESS) {
// // 	    PJ_LOG(1,(THIS_FILE, "    encode error: %s", err(status)));
// // 	    rc = -40;
// // 	    goto on_return;
// // 	}
// // 
// // 	/* Try to decode it once more */
// // 	status = pj_stun_msg_decode(pool, buf, len, 
// // 				    PJ_STUN_IS_DATAGRAM | PJ_STUN_CHECK_PACKET, 
// // 				    &msg2, NULL, NULL);
// // 	if (status != PJ_SUCCESS) {
// // 	    PJ_LOG(1,(THIS_FILE, "    subsequent decoding failed: %s", err(status)));
// // 	    rc = -50;
// // 	    goto on_return;
// // 	}
// // 
// // 	/* Verify */
// // 	if (t->verify) {
// // 	    rc = t->verify(msg);
// // 	    if (rc != 0) {
// // 		goto on_return;
// // 	    }
// // 	}
// //     }
// // 
// // on_return:
// //     pj_pool_release(pool);
// //     if (rc == 0)
// // 	PJ_LOG(3,(THIS_FILE, "...success!"));
// //     return rc;
// // }
// 
// 
// Based on the above information, fix the code.
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    pj_caching_pool cp;
    pj_pool_t *pool;
    pj_stun_msg *msg;

    pj_caching_pool_init(&cp, NULL, 0);
    pool = pj_pool_create(&cp.factory, "pool", 512, 512, NULL);
    if (!pool) {
        return 0;
    }

    if (!Data || !Size) {
        pj_pool_release(pool);
        pj_caching_pool_destroy(&cp);
        return 0;
    }

    pj_status_t status = pj_stun_msg_decode(pool, Data, Size, PJ_STUN_IS_DATAGRAM | PJ_STUN_CHECK_PACKET, &msg, NULL, NULL);
    pj_pool_release(pool);
    pj_caching_pool_destroy(&cp);

    return 0;
}