#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>

#include "hf.h"
#include "keys.h"
#include "msg_parser.h"
#include "parse_addr_spec.h"
#include "parse_allow.h"
#include "parse_body.h"
#include "parse_content.h"
#include "parse_cseq.h"
#include "parse_date.h"
#include "parse_def.h"
#include "parse_disposition.h"
#include "parse_diversion.h"
#include "parse_event.h"
#include "parse_expires.h"
#include "parse_fline.h"
#include "parse_from.h"
#include "parse_hname2.h"
#include "parse_identity.h"
#include "parse_identityinfo.h"
#include "parse_methods.h"
#include "parse_nameaddr.h"
#include "parse_option_tags.h"
#include "parse_param.h"
#include "parse_ppi_pai.h"
#include "parse_privacy.h"
#include "parse_refer_to.h"
#include "parse_require.h"
#include "parse_retry_after.h"
#include "parse_rpid.h"
#include "parse_rr.h"
#include "parse_sipifmatch.h"
#include "parse_subscription_state.h"
#include "parse_supported.h"
#include "parse_to.h"
#include "parse_uri.h"
#include "parse_via.h"
#include "parser_f.h"

// ```
// #include "parse_addr_spec.h"
// 
// //extern sip_uri_t * parse_to_uri(struct sip_msg *const msg);
// 
// // the following function fuzzes parse_to_uri
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//     sip_uri_t *uri;
//     struct sip_msg msg;
// 
//     // Initialize the SIP message buffer.
//     memset(&msg, 0, sizeof(msg));
// 
//     // Cast the fuzz input data to a string and set it as the SIP message buffer's content.
//     msg.buf = (char *)Data;
//     msg.len = Size;
// 
//     // Make sure the sip_msg structure and its members are defined properly
//     if (!msg.buf)
//     {
//         return 0;
//     }
// 
//     // Check if the input data is a valid SIP message.
//     if (parse_msg(msg.buf, msg.len, &msg) != 0)
//     {
//         // Free the allocated resources.
//         free_sip_msg(&msg);
// 
//         // If the input is not a valid SIP message, return 0 (no crash).
//         return 0;
//     }
// 
//     // Call the actual function that will be fuzzed.
//     uri = parse_to_uri(&msg);
// 
//     // To free uri, first free uri->user and uri->host since they were allocated in parse_to_uri
//     if (uri) {
//         if (uri->user) {
//             pkg_free(uri->user);
//         }
//         if (uri->host) {
//             pkg_free(uri->host);
//         }
//         // Now free the sip_uri object itself
//         pkg_free(uri);
//     }
// 
//     // Free the allocated resources.
//     free_sip_msg(&msg);
// 
//     // If the fuzzer reached this point, there was no crash or failure.
//     return 0;
// }
// ```
// 
// The above C code has compilation error.
// The error line is:
// if (uri->user) {
// 
// The error description is:
// statement requires expression of scalar type ('str' (aka 'struct _str') invalid)
// 
// Based on the above information, fix the code.
#include "parse_addr_spec.h"

//extern sip_uri_t * parse_to_uri(struct sip_msg *const msg);

// the following function fuzzes parse_to_uri
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    sip_uri_t *uri;
    struct sip_msg msg;

    // Initialize the SIP message buffer.
    memset(&msg, 0, sizeof(msg));

    // Cast the fuzz input data to a string and set it as the SIP message buffer's content.
    msg.buf = (char *)Data;
    msg.len = Size;

    // Make sure the sip_msg structure and its members are defined properly
    if (!msg.buf)
    {
        return 0;
    }

    // Check if the input data is a valid SIP message.
    if (parse_msg(msg.buf, msg.len, &msg) != 0)
    {
        // Free the allocated resources.
        free_sip_msg(&msg);

        // If the input is not a valid SIP message, return 0 (no crash).
        return 0;
    }

    // Call the actual function that will be fuzzed.
    uri = parse_to_uri(&msg);

    // To free uri, first free uri->user and uri->host since they were allocated in parse_to_uri
    if (uri) {
        if (uri->user.s) { // Changed from uri->user to uri->user.s
            pkg_free(uri->user.s); // Changed from uri->user to uri->user.s
        }
        if (uri->host.s) { // Changed from uri->host to uri->host.s
            pkg_free(uri->host.s); // Changed from uri->host to uri->host.s
        }
        // Now free the sip_uri object itself
        pkg_free(uri);
    }

    // Free the allocated resources.
    free_sip_msg(&msg);

    // If the fuzzer reached this point, there was no crash or failure.
    return 0;
}