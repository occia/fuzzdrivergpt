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

// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.

#include "msg_parser.h"

// @ examples of API usage from kamailio/kamailio/src/modules/gzcompress/gzcompress_mod.c-gzc_prepare_msg
// int gzc_prepare_msg(sip_msg_t *msg)
// {
// 	if (parse_msg(msg->buf, msg->len, msg)!=0)
// 	{
// 		LM_DBG("outbuf buffer parsing failed!");
// 		return 1;
// 	}
// 
// 	if(msg->first_line.type==SIP_REQUEST)
// 	{
// 		if(!IS_SIP(msg) && !IS_HTTP(msg))
// 		{
// 			LM_DBG("non sip or http request\n");
// 			return 1;
// 		}
// 	} else if(msg->first_line.type==SIP_REPLY) {
// 		if(!IS_SIP_REPLY(msg) && !IS_HTTP_REPLY(msg))
// 		{
// 			LM_DBG("non sip or http response\n");
// 			return 1;
// 		}
// 	} else {
// 		LM_DBG("non sip or http message\n");
// 		return 1;
// 	}
// 
// 	if (parse_headers(msg, HDR_EOH_F, 0)==-1)
// 	{
// 		LM_DBG("parsing headers failed");
// 		return 2;
// 	}
// 
// 	return 0;
// }

//extern int parse_headers(struct sip_msg *const msg,const hdr_flags_t flags,const int next);
//extern int parse_msg(char *const buf,const unsigned int len,struct sip_msg *const msg);

// the following function fuzzes parse_msg based on the above API usages
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
// Complete the implementation of the fuzz driver:

    // Create a new sip_msg_t structure
    struct sip_msg *msg = (struct sip_msg *)malloc(sizeof(struct sip_msg));
    
    // Set the buffer and length of the message
    msg->buf = (char *)Data;
    msg->len = Size;
    
    // Call parse_msg to parse the message buffer
    if (parse_msg(msg->buf, msg->len, msg) != 0) {
        LM_DBG("outbuf buffer parsing failed!");
        free(msg);
        return 1;
    }
    
    // Check the message type
    if (msg->first_line.type == SIP_REQUEST) {
        // Check if the request is SIP or HTTP
        if (!IS_SIP(msg) && !IS_HTTP(msg)) {
            LM_DBG("non sip or http request\n");
            free(msg);
            return 1;
        }
    } else if (msg->first_line.type == SIP_REPLY) {
        // Check if the response is SIP or HTTP
        if (!IS_SIP_REPLY(msg) && !IS_HTTP_REPLY(msg)) {
            LM_DBG("non sip or http response\n");
            free(msg);
            return 1;
        }
    } else {
        LM_DBG("non sip or http message\n");
        free(msg);
        return 1;
    }
    
    // Parse the headers
    if (parse_headers(msg, HDR_EOH_F, 0) == -1) {
        LM_DBG("parsing headers failed");
        free(msg);
        return 2;
    }
    
    // Cleanup and return
    free(msg);
    return 0;
}