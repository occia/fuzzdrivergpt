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
// #include "parse_from.h"
// 
// // @ examples of API usage from src/kamailio/src/modules/topoh/topoh_mod.c-th_prepare_msg
// // int th_prepare_msg(sip_msg_t *msg)
// // {
// // 	if (parse_msg(msg->buf, msg->len, msg)!=0)
// // 	{
// // 		LM_DBG("outbuf buffer parsing failed!");
// // 		return 1;
// // 	}
// // 
// // 	if(msg->first_line.type==SIP_REQUEST)
// // 	{
// // 		if(!IS_SIP(msg))
// // 		{
// // 			LM_DBG("non sip request message\n");
// // 			return 1;
// // 		}
// // 	} else if(msg->first_line.type==SIP_REPLY) {
// // 		if(!IS_SIP_REPLY(msg))
// // 		{
// // 			LM_DBG("non sip reply message\n");
// // 			return 1;
// // 		}
// // 	} else {
// // 		LM_DBG("unknown sip message type %d\n", msg->first_line.type);
// // 		return 1;
// // 	}
// // 
// // 	if (parse_headers(msg, HDR_EOH_F, 0)==-1)
// // 	{
// // 		LM_DBG("parsing headers failed [[%.*s]]\n",
// // 				msg->len, msg->buf);
// // 		return 2;
// // 	}
// // 
// // 	/* force 2nd via parsing here - it helps checking it later */
// // 	if (parse_headers(msg, HDR_VIA2_F, 0)==-1
// // 		|| (msg->via2==0) || (msg->via2->error!=PARSE_OK))
// // 	{
// // 		LM_DBG("no second via in this message \n");
// // 	}
// // 
// // 	if(parse_from_header(msg)<0)
// // 	{
// // 		LM_ERR("cannot parse FROM header\n");
// // 		return 3;
// // 	}
// // 
// // 	if(parse_to_header(msg)<0 || msg->to==NULL)
// // 	{
// // 		LM_ERR("cannot parse TO header\n");
// // 		return 3;
// // 	}
// // 
// // 	if(get_to(msg)==NULL)
// // 	{
// // 		LM_ERR("cannot get TO header\n");
// // 		return 3;
// // 	}
// // 
// // 	if(msg->via1==NULL || msg->callid==NULL) {
// // 		LM_ERR("mandatory headers missing - via1: %p callid: %p\n",
// // 				msg->via1, msg->callid);
// // 		return 4;
// // 	}
// // 
// // 	return 0;
// // }
// 
// //extern int parse_headers(struct sip_msg *const msg,const hdr_flags_t flags,const int next);
// //extern int parse_from_header(struct sip_msg * msg);
// //extern int parse_msg(char *const buf,const unsigned int len,struct sip_msg *const msg);
// //extern int parse_to_header(struct sip_msg *const msg);
// 
// // the following function fuzzes parse_from_header based on the above API usages
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
// // Include the necessary header files
// #include "parse_from.h"
// 
// // Define the external functions
// extern int parse_headers(struct sip_msg *const msg, const hdr_flags_t flags, const int next);
// extern int parse_from_header(struct sip_msg *msg);
// extern int parse_msg(char *const buf, const unsigned int len, struct sip_msg *const msg);
// extern int parse_to_header(struct sip_msg *const msg);
// 
// // Implement the LLVMFuzzerTestOneInput function
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//     // Create a sip_msg structure
//     struct sip_msg *msg = (struct sip_msg *)malloc(sizeof(struct sip_msg));
// 
//     // Check if memory allocation was successful
//     if (msg == NULL) {
//         return 1;
//     }
// 
//     // Initialize the sip_msg structure
//     memset(msg, 0, sizeof(struct sip_msg));
// 
//     // Create a buffer to hold the input data
//     char *buf = (char *)malloc(Size + 1);
// 
//     // Check if memory allocation was successful
//     if (buf == NULL) {
//         free(msg);
//         return 1;
//     }
// 
//     // Copy the input data into the buffer
//     memcpy(buf, Data, Size);
//     buf[Size] = '\0';
// 
//     // Call the parse_msg function to parse the message
//     if (parse_msg(buf, Size, msg) != 0) {
//         // Parsing failed
//         free(buf);
//         free(msg);
//         return 1;
//     }
// 
//     // Check the message type
//     if (msg->first_line.type == SIP_REQUEST) {
//         // Check if it is a SIP request
//         if (!IS_SIP(msg)) {
//             free(buf);
//             free(msg);
//             return 1;
//         }
//     } else if (msg->first_line.type == SIP_REPLY) {
//         // Check if it is a SIP reply
//         if (!IS_SIP_REPLY(msg)) {
//             free(buf);
//             free(msg);
//             return 1;
//         }
//     } else {
//         // Unknown SIP message type
//         free(buf);
//         free(msg);
//         return 1;
//     }
// 
//     // Parse the headers
//     if (parse_headers(msg, HDR_EOH_F, 0) == -1) {
//         free(buf);
//         free(msg);
//         return 2;
//     }
// 
//     // Parse the second Via header
//     if (parse_headers(msg, HDR_VIA2_F, 0) == -1 || (msg->via2 == 0) || (msg->via2->error != PARSE_OK)) {
//         // Second Via header not found
//     }
// 
//     // Parse the FROM header
//     if (parse_from_header(msg) < 0) {
//         free(buf);
//         free(msg);
//         return 3;
//     }
// 
//     // Parse the TO header
//     if (parse_to_header(msg) < 0 || msg->to == NULL) {
//         free(buf);
//         free(msg);
//         return 3;
//     }
// 
//     // Get the TO header
//     if (get_to(msg) == NULL) {
//         free(buf);
//         free(msg);
//         return 3;
//     }
// 
//     // Check if mandatory headers are missing
//     if (msg->via1 == NULL || msg->callid == NULL) {
//         free(buf);
//         free(msg);
//         return 4;
//     }
// 
//     // Cleanup
//     free(buf);
//     free(msg);
// 
//     return 0;
// }
// ```
// 
// The above C code has compilation error.
// The error line is:
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
// 
// The error description is:
// function definition is not allowed here
// 
// The definition of `parse_headers`:
// extern int parse_headers(struct sip_msg *const msg,const hdr_flags_t flags,const int next);
// 
// // @ examples of API `parse_headers` usage from /tmp/sourcegraph_tmpdir/github.com/kamailio/kamailio/src/core/id.c
// // int get_to_uid(str* uid, struct sip_msg* msg)
// // {
// // 	static char buf[MAX_URI_SIZE];
// // 	struct to_body* to;
// // 	struct sip_uri puri;
// // 	char* p;
// // 	int_str val, name;
// // 
// // 	name.s = uid_name;
// // 	if (search_first_avp(AVP_CLASS_USER | AVP_TRACK_TO | AVP_NAME_STR, name, &val, 0)) {
// // 		*uid = val.s;
// // 		return 1;
// // 	} else {
// // 		if (msg->REQ_METHOD == METHOD_REGISTER) {
// // 			if ((msg->to==0) && 
// // 				(parse_headers(msg, HDR_TO_F, 0) < 0 || msg->to == 0)) {
// // 				LM_DBG("Error while parsing To URI: to header bad or missing\n");
// // 				return -1;
// // 			}
// // 			to = get_to(msg);
// // 			if (parse_uri(to->uri.s, to->uri.len, &puri) == -1) {
// // 				LM_DBG("Error while parsing To URI\n");
// // 				return -1;
// // 			}
// // 			p = puri.user.s;
// // 			uid->len = puri.user.len;
// // 		} else {
// // 			if (!msg->parsed_uri_ok && (parse_sip_msg_uri(msg) < 0)) {
// // 				LM_DBG("Error while parsing the Request-URI\n");
// // 				return -1;
// // 			}
// // 			p = msg->parsed_uri.user.s;
// // 			uid->len = msg->parsed_uri.user.len;
// // 		}
// // 			
// // 		if (uid->len > MAX_URI_SIZE) {
// // 			LM_DBG("Username too long\n");
// // 			return -1;
// // 		}
// // 		if (p == NULL || uid->len == 0) {
// // 			LM_DBG("Username is empty\n");
// // 			return -1;
// // 		}
// // 		memcpy(buf, p, uid->len);
// // 		uid->s = buf;
// // 		strlower(uid);
// // 
// // 		val.s = *uid;
// // 		add_avp(AVP_CLASS_USER | AVP_TRACK_TO | AVP_NAME_STR | AVP_VAL_STR, name, val);
// // 		return 0;
// // 	}
// // }
// 
// 
// Based on the above information, fix the code.
#include <stdlib.h>
#include <string.h>
#include "parse_from.h"

// Define the external functions
extern extern int parse_headers(struct sip_msg *const msg, const hdr_flags_t flags, const int next);
extern extern int parse_from_header(struct sip_msg *msg);
extern extern int parse_msg(char *const buf, const unsigned int len, struct sip_msg *const msg);
extern extern int parse_to_header(struct sip_msg *const msg);

// Implement the LLVMFuzzerTestOneInput function
int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    // Create a sip_msg structure
    struct sip_msg *msg = (struct sip_msg *)malloc(sizeof(struct sip_msg));

    // Check if memory allocation was successful
    if (msg == NULL) {
        return 1;
    }

    // Initialize the sip_msg structure
    memset(msg, 0, sizeof(struct sip_msg));

    // Create a buffer to hold the input data
    char *buf = (char *)malloc(Size + 1);

    // Check if memory allocation was successful
    if (buf == NULL) {
        free(msg);
        return 1;
    }

    // Copy the input data into the buffer
    memcpy(buf, Data, Size);
    buf[Size] = '\0';

    // Call the parse_msg function to parse the message
    if (parse_msg(buf, Size, msg) != 0) {
        // Parsing failed
        free(buf);
        free(msg);
        return 1;
    }

    // Check the message type
    if (msg->first_line.type == SIP_REQUEST) {
        // Check if it is a SIP request
        if (!IS_SIP(msg)) {
            free(buf);
            free(msg);
            return 1;
        }
    } else if (msg->first_line.type == SIP_REPLY) {
        // Check if it is a SIP reply
        if (!IS_SIP_REPLY(msg)) {
            free(buf);
            free(msg);
            return 1;
        }
    } else {
        // Unknown SIP message type
        free(buf);
        free(msg);
        return 1;
    }

    // Parse the headers
    if (parse_headers(msg, HDR_EOH_F, 0) == -1) {
        free(buf);
        free(msg);
        return 2;
    }

    // Parse the second Via header
    if (parse_headers(msg, HDR_VIA2_F, 0) == -1 || (msg->via2 == 0) || (msg->via2->error != PARSE_OK)) {
        // Second Via header not found
    }

    // Parse the FROM header
    if (parse_from_header(msg) < 0) {
        free(buf);
        free(msg);
        return 3;
    }

    // Parse the TO header
    if (parse_to_header(msg) < 0 || msg->to == NULL) {
        free(buf);
        free(msg);
        return 3;
    }

    // Get the TO header
    if (get_to(msg) == NULL) {
        free(buf);
        free(msg);
        return 3;
    }

    // Check if mandatory headers are missing
    if (msg->via1 == NULL || msg->callid == NULL) {
        free(buf);
        free(msg);
        return 4;
    }

    // Cleanup
    free(buf);
    free(msg);

    return 0;
}