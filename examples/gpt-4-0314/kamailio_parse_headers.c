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

// @ examples of API usage from src/kamailio/src/modules/topoh/topoh_mod.c-th_prepare_msg
// int th_prepare_msg(sip_msg_t *msg)
// {
// 	if (parse_msg(msg->buf, msg->len, msg)!=0)
// 	{
// 		LM_DBG("outbuf buffer parsing failed!");
// 		return 1;
// 	}
// 
// 	if(msg->first_line.type==SIP_REQUEST)
// 	{
// 		if(!IS_SIP(msg))
// 		{
// 			LM_DBG("non sip request message\n");
// 			return 1;
// 		}
// 	} else if(msg->first_line.type==SIP_REPLY) {
// 		if(!IS_SIP_REPLY(msg))
// 		{
// 			LM_DBG("non sip reply message\n");
// 			return 1;
// 		}
// 	} else {
// 		LM_DBG("unknown sip message type %d\n", msg->first_line.type);
// 		return 1;
// 	}
// 
// 	if (parse_headers(msg, HDR_EOH_F, 0)==-1)
// 	{
// 		LM_DBG("parsing headers failed [[%.*s]]\n",
// 				msg->len, msg->buf);
// 		return 2;
// 	}
// 
// 	/* force 2nd via parsing here - it helps checking it later */
// 	if (parse_headers(msg, HDR_VIA2_F, 0)==-1
// 		|| (msg->via2==0) || (msg->via2->error!=PARSE_OK))
// 	{
// 		LM_DBG("no second via in this message \n");
// 	}
// 
// 	if(parse_from_header(msg)<0)
// 	{
// 		LM_ERR("cannot parse FROM header\n");
// 		return 3;
// 	}
// 
// 	if(parse_to_header(msg)<0 || msg->to==NULL)
// 	{
// 		LM_ERR("cannot parse TO header\n");
// 		return 3;
// 	}
// 
// 	if(get_to(msg)==NULL)
// 	{
// 		LM_ERR("cannot get TO header\n");
// 		return 3;
// 	}
// 
// 	if(msg->via1==NULL || msg->callid==NULL) {
// 		LM_ERR("mandatory headers missing - via1: %p callid: %p\n",
// 				msg->via1, msg->callid);
// 		return 4;
// 	}
// 
// 	return 0;
// }

//extern int parse_headers(struct sip_msg *const msg,const hdr_flags_t flags,const int next);
//extern int parse_from_header(struct sip_msg * msg);
//extern int parse_msg(char *const buf,const unsigned int len,struct sip_msg *const msg);
//extern int parse_to_header(struct sip_msg *const msg);

// the following function fuzzes parse_headers based on the above API usages
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
struct sip_msg msg;
    hdr_flags_t flags;
    int next;

    if (Size < sizeof(hdr_flags_t) + sizeof(int)) {
        return 0;
    }

    memcpy(&flags, Data, sizeof(hdr_flags_t));
    Data += sizeof(hdr_flags_t);
    Size -= sizeof(hdr_flags_t);

    memcpy(&next, Data, sizeof(int));
    Data += sizeof(int);
    Size -= sizeof(int);

    msg.buf = (char *)Data;
    msg.len = Size;

    if (parse_msg(msg.buf, msg.len, &msg) != 0) {
        return 0;
    }

    if(parse_headers(&msg, flags, next) == -1) {
        return 0;
    }

    if(parse_from_header(&msg) < 0) {
        return 0;
    }

    if(parse_to_header(&msg) < 0) {
        return 0;
    }

    return 0;
}