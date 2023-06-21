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

// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.

//#include "pjmedia/sdp.h"

// @ examples of API usage from pjproject/pjsip/src/pjsip-ua/sip_inv.c-inv_check_sdp_in_incoming_msg
// static pj_status_t inv_check_sdp_in_incoming_msg( pjsip_inv_session *inv,
// 						  pjsip_transaction *tsx,
// 						  pjsip_rx_data *rdata)
// {
//     struct tsx_inv_data *tsx_inv_data;
//     static const pj_str_t str_application = { "application", 11 };
//     static const pj_str_t str_sdp = { "sdp", 3 };
//     pj_status_t status;
//     pjsip_msg *msg;
//     pjmedia_sdp_session *rem_sdp;
// 
//     /* Check if SDP is present in the message. */
// 
//     msg = rdata->msg_info.msg;
//     if (msg->body == NULL) {
// 	/* Message doesn't have body. */
// 	return PJ_SUCCESS;
//     }
// 
//     if (pj_stricmp(&msg->body->content_type.type, &str_application) ||
// 	pj_stricmp(&msg->body->content_type.subtype, &str_sdp))
//     {
// 	/* Message body is not "application/sdp" */
// 	return PJMEDIA_SDP_EINSDP;
//     }
// 
//     /* Get/attach invite session's transaction data */
//     tsx_inv_data = (struct tsx_inv_data*) tsx->mod_data[mod_inv.mod.id];
//     if (tsx_inv_data == NULL) {
// 	tsx_inv_data = PJ_POOL_ZALLOC_T(tsx->pool, struct tsx_inv_data);
// 	tsx_inv_data->inv = inv;
// 	tsx->mod_data[mod_inv.mod.id] = tsx_inv_data;
//     }
// 
//     /* MUST NOT do multiple SDP offer/answer in a single transaction,
//      * EXCEPT if:
//      *	- this is an initial UAC INVITE transaction (i.e. not re-INVITE), and
//      *	- the previous negotiation was done on an early media (18x) and
//      *    this response is a final/2xx response, and
//      *  - the 2xx response has different To tag than the 18x response
//      *    (i.e. the request has forked).
//      *
//      * The exception above is to add a rudimentary support for early media
//      * forking (sample case: custom ringback). See this ticket for more
//      * info: http://trac.pjsip.org/repos/ticket/657
//      */
//     if (tsx_inv_data->sdp_done) {
// 	pj_str_t res_tag;
// 
// 	res_tag = rdata->msg_info.to->tag;
// 
// 	/* Allow final response after SDP has been negotiated in early
// 	 * media, IF this response is a final response with different
// 	 * tag.
// 	 */
// 	if (tsx->role == PJSIP_ROLE_UAC &&
// 	    rdata->msg_info.msg->line.status.code/100 == 2 &&
// 	    tsx_inv_data->done_early &&
// 	    pj_strcmp(&tsx_inv_data->done_tag, &res_tag))
// 	{
// 	    const pjmedia_sdp_session *reoffer_sdp = NULL;
// 
// 	    PJ_LOG(4,(inv->obj_name, "Received forked final response "
// 		      "after SDP negotiation has been done in early "
// 		      "media. Renegotiating SDP.."));
// 
// 	    /* Retrieve original SDP offer from INVITE request */
// 	    reoffer_sdp = (const pjmedia_sdp_session*) 
// 			  tsx->last_tx->msg->body->data;
// 
// 	    /* Feed the original offer to negotiator */
// 	    status = pjmedia_sdp_neg_modify_local_offer(inv->pool_prov, 
// 							inv->neg,
// 						        reoffer_sdp);
// 	    if (status != PJ_SUCCESS) {
// 		PJ_LOG(1,(inv->obj_name, "Error updating local offer for "
// 			  "forked 2xx response (err=%d)", status));
// 		return status;
// 	    }
// 
// 	} else {
// 
// 	    if (rdata->msg_info.msg->body) {
// 		PJ_LOG(4,(inv->obj_name, "SDP negotiation done, message "
// 			  "body is ignored"));
// 	    }
// 	    return PJ_SUCCESS;
// 	}
//     }
// 
//     /* Parse the SDP body. */
// 
//     status = pjmedia_sdp_parse(rdata->tp_info.pool, 
// 			       (char*)msg->body->data,
// 			       msg->body->len, &rem_sdp);
//     if (status == PJ_SUCCESS)
// 	status = pjmedia_sdp_validate(rem_sdp);
// 
//     if (status != PJ_SUCCESS) {
// 	char errmsg[PJ_ERR_MSG_SIZE];
// 	pj_strerror(status, errmsg, sizeof(errmsg));
// 	PJ_LOG(4,(THIS_FILE, "Error parsing SDP in %s: %s",
// 		  pjsip_rx_data_get_info(rdata), errmsg));
// 	return PJMEDIA_SDP_EINSDP;
//     }
// 
//     /* The SDP can be an offer or answer, depending on negotiator's state */
// 
//     if (inv->neg == NULL ||
// 	pjmedia_sdp_neg_get_state(inv->neg) == PJMEDIA_SDP_NEG_STATE_DONE) 
//     {
// 
// 	/* This is an offer. */
// 
// 	PJ_LOG(5,(inv->obj_name, "Got SDP offer in %s", 
// 		  pjsip_rx_data_get_info(rdata)));
// 
// 	if (inv->neg == NULL) {
// 	    status=pjmedia_sdp_neg_create_w_remote_offer(inv->pool, NULL,
// 							 rem_sdp, &inv->neg);
// 	} else {
// 	    status=pjmedia_sdp_neg_set_remote_offer(inv->pool_prov, inv->neg, 
// 						    rem_sdp);
// 	}
// 
// 	if (status != PJ_SUCCESS) {
// 	    char errmsg[PJ_ERR_MSG_SIZE];
// 	    pj_strerror(status, errmsg, sizeof(errmsg));
// 	    PJ_LOG(4,(THIS_FILE, "Error processing SDP offer in %s: %s",
// 		      pjsip_rx_data_get_info(rdata), errmsg));
// 	    return PJMEDIA_SDP_EINSDP;
// 	}
// 
// 	/* Inform application about remote offer. */
// 
// 	if (mod_inv.cb.on_rx_offer && inv->notify) {
// 
// 	    (*mod_inv.cb.on_rx_offer)(inv, rem_sdp);
// 
// 	}
// 
//     } else if (pjmedia_sdp_neg_get_state(inv->neg) == 
// 		PJMEDIA_SDP_NEG_STATE_LOCAL_OFFER) 
//     {
// 	int status_code;
// 
// 	/* This is an answer. 
// 	 * Process and negotiate remote answer.
// 	 */
// 
// 	PJ_LOG(5,(inv->obj_name, "Got SDP answer in %s", 
// 		  pjsip_rx_data_get_info(rdata)));
// 
// 	status = pjmedia_sdp_neg_set_remote_answer(inv->pool_prov, inv->neg,
// 						   rem_sdp);
// 
// 	if (status != PJ_SUCCESS) {
// 	    char errmsg[PJ_ERR_MSG_SIZE];
// 	    pj_strerror(status, errmsg, sizeof(errmsg));
// 	    PJ_LOG(4,(THIS_FILE, "Error processing SDP answer in %s: %s",
// 		      pjsip_rx_data_get_info(rdata), errmsg));
// 	    return PJMEDIA_SDP_EINSDP;
// 	}
// 
// 	/* Negotiate SDP */
// 
// 	inv_negotiate_sdp(inv);
// 
// 	/* Mark this transaction has having SDP offer/answer done, and
// 	 * save the reference to the To tag
// 	 */
// 
// 	tsx_inv_data->sdp_done = 1;
// 	status_code = rdata->msg_info.msg->line.status.code;
// 	tsx_inv_data->done_early = (status_code/100==1);
// 	pj_strdup(tsx->pool, &tsx_inv_data->done_tag, 
// 		  &rdata->msg_info.to->tag);
// 
//     } else {
// 	
// 	PJ_LOG(5,(THIS_FILE, "Ignored SDP in %s: negotiator state is %s",
// 	      pjsip_rx_data_get_info(rdata), 
// 	      pjmedia_sdp_neg_state_str(pjmedia_sdp_neg_get_state(inv->neg))));
//     }
// 
//     return PJ_SUCCESS;
// }

//extern pj_status_t pjmedia_sdp_neg_modify_local_offer(pj_pool_t * pool,pjmedia_sdp_neg * neg,const pjmedia_sdp_session * local);
//extern char * pjsip_rx_data_get_info(pjsip_rx_data * rdata);
//extern int pj_strcmp(const pj_str_t * str1,const pj_str_t * str2);
//extern int pj_stricmp(const pj_str_t * str1,const pj_str_t * str2);
//extern pj_str_t pj_strerror(pj_status_t statcode,char * buf,pj_size_t bufsize);
//extern pj_status_t pjmedia_sdp_neg_set_remote_offer(pj_pool_t * pool,pjmedia_sdp_neg * neg,const pjmedia_sdp_session * remote);
//extern pjmedia_sdp_neg_state pjmedia_sdp_neg_get_state(pjmedia_sdp_neg * neg);
//extern pj_str_t * pj_strdup(pj_pool_t * pool,pj_str_t * dst,const pj_str_t * src);
//extern const char * pjmedia_sdp_neg_state_str(pjmedia_sdp_neg_state state);
//extern pj_status_t pjmedia_sdp_neg_create_w_remote_offer(pj_pool_t * pool,const pjmedia_sdp_session * initial,const pjmedia_sdp_session * remote,pjmedia_sdp_neg ** p_neg);
//extern pj_status_t pjmedia_sdp_neg_set_remote_answer(pj_pool_t * pool,pjmedia_sdp_neg * neg,const pjmedia_sdp_session * remote);
//extern pj_status_t pjmedia_sdp_validate(const pjmedia_sdp_session * sdp);
//extern pj_status_t pjmedia_sdp_parse(pj_pool_t * pool,char * buf,pj_size_t len,pjmedia_sdp_session ** p_sdp);

// the following function fuzzes pjmedia_sdp_parse based on the above API usages
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
pj_pool_t *pool;
    pjmedia_sdp_session *sdp;
    pj_status_t status;

    // create pool factory
    pj_caching_pool cp;
    pj_caching_pool_init(&cp, NULL, 0);

    // create memory pool
    pool = pj_pool_create(&cp.factory, "sdp_parser_pool", 1000, 1000, NULL);

    // ensure data is null-terminated
    char *data_str = (char *)pj_pool_alloc(pool, Size + 1);
    memcpy(data_str, Data, Size);
    data_str[Size] = '\0';

    // parse sdp
    status = pjmedia_sdp_parse(pool, data_str, Size, &sdp);

    if (status == PJ_SUCCESS) {
        // validate sdp
        status = pjmedia_sdp_validate(sdp);
    }

    // release memory pool
    pj_pool_release(pool);

    return 0;
}