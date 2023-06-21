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

// @ examples of API usage from pjproject/pjsip/src/pjsip-ua/sip_inv.c-pjsip_inv_create_uas
// PJ_DEF(pj_status_t) pjsip_inv_create_uas( pjsip_dialog *dlg,
// 					  pjsip_rx_data *rdata,
// 					  const pjmedia_sdp_session *local_sdp,
// 					  unsigned options,
// 					  pjsip_inv_session **p_inv)
// {
//     pjsip_inv_session *inv;
//     struct tsx_inv_data *tsx_inv_data;
//     pjsip_msg *msg;
//     pjmedia_sdp_session *rem_sdp = NULL;
//     pj_status_t status;
// 
//     /* Verify arguments. */
//     PJ_ASSERT_RETURN(dlg && rdata && p_inv, PJ_EINVAL);
// 
//     /* Dialog MUST have been initialised. */
//     PJ_ASSERT_RETURN(pjsip_rdata_get_tsx(rdata) != NULL, PJ_EINVALIDOP);
// 
//     msg = rdata->msg_info.msg;
// 
//     /* rdata MUST contain INVITE request */
//     PJ_ASSERT_RETURN(msg->type == PJSIP_REQUEST_MSG &&
// 		     msg->line.req.method.id == PJSIP_INVITE_METHOD,
// 		     PJ_EINVALIDOP);
// 
//     /* Lock dialog */
//     pjsip_dlg_inc_lock(dlg);
// 
//     /* Normalize options */
//     if (options & PJSIP_INV_REQUIRE_100REL)
// 	options |= PJSIP_INV_SUPPORT_100REL;
//     if (options & PJSIP_INV_REQUIRE_TIMER)
// 	options |= PJSIP_INV_SUPPORT_TIMER;
// 
//     /* Create the session */
//     inv = PJ_POOL_ZALLOC_T(dlg->pool, pjsip_inv_session);
//     pj_assert(inv != NULL);
// 
//     inv->pool = dlg->pool;
//     inv->role = PJSIP_ROLE_UAS;
//     inv->state = PJSIP_INV_STATE_NULL;
//     inv->dlg = dlg;
//     inv->options = options;
//     inv->notify = PJ_TRUE;
//     inv->cause = (pjsip_status_code) 0;
// 
//     /* Create flip-flop pool (see ticket #877) */
//     /* (using inv->obj_name as temporary variable for pool names */
//     pj_ansi_snprintf(inv->obj_name, PJ_MAX_OBJ_NAME, "inv%p", dlg->pool);
//     inv->pool_prov = pjsip_endpt_create_pool(dlg->endpt, inv->obj_name,
// 					     POOL_INIT_SIZE, POOL_INC_SIZE);
//     inv->pool_active = pjsip_endpt_create_pool(dlg->endpt, inv->obj_name,
// 					       POOL_INIT_SIZE, POOL_INC_SIZE);
// 
//     /* Object name will use the same dialog pointer. */
//     pj_ansi_snprintf(inv->obj_name, PJ_MAX_OBJ_NAME, "inv%p", dlg);
// 
//     /* Parse SDP in message body, if present. */
//     if (msg->body) {
// 	pjsip_msg_body *body = msg->body;
// 
// 	/* Parse and validate SDP */
// 	status = pjmedia_sdp_parse(inv->pool, (char*)body->data, body->len,
// 				   &rem_sdp);
// 	if (status == PJ_SUCCESS)
// 	    status = pjmedia_sdp_validate(rem_sdp);
// 
// 	if (status != PJ_SUCCESS) {
// 	    pjsip_dlg_dec_lock(dlg);
// 	    return status;
// 	}
//     }
// 
//     /* Create negotiator. */
//     if (rem_sdp) {
// 	status = pjmedia_sdp_neg_create_w_remote_offer(inv->pool, 
// 						       local_sdp, rem_sdp, 
// 						       &inv->neg);
// 						
//     } else if (local_sdp) {
// 	status = pjmedia_sdp_neg_create_w_local_offer(inv->pool, 
// 						      local_sdp, &inv->neg);
//     } else {
// 	status = PJ_SUCCESS;
//     }
// 
//     if (status != PJ_SUCCESS) {
// 	pjsip_dlg_dec_lock(dlg);
// 	return status;
//     }
// 
//     /* Register invite as dialog usage. */
//     status = pjsip_dlg_add_usage(dlg, &mod_inv.mod, inv);
//     if (status != PJ_SUCCESS) {
// 	pjsip_dlg_dec_lock(dlg);
// 	return status;
//     }
// 
//     /* Increment session in the dialog. */
//     pjsip_dlg_inc_session(dlg, &mod_inv.mod);
// 
//     /* Save the invite transaction. */
//     inv->invite_tsx = pjsip_rdata_get_tsx(rdata);
// 
//     /* Attach our data to the transaction. */
//     tsx_inv_data = PJ_POOL_ZALLOC_T(inv->invite_tsx->pool, struct tsx_inv_data);
//     tsx_inv_data->inv = inv;
//     inv->invite_tsx->mod_data[mod_inv.mod.id] = tsx_inv_data;
// 
//     /* Create 100rel handler */
//     if (inv->options & PJSIP_INV_REQUIRE_100REL) {
// 	pjsip_100rel_attach(inv);
//     }
// 
//     /* Done */
//     pjsip_dlg_dec_lock(dlg);
//     *p_inv = inv;
// 
//     PJ_LOG(5,(inv->obj_name, "UAS invite session created for dialog %s",
// 	      dlg->obj_name));
// 
//     return PJ_SUCCESS;
// }

//extern pj_status_t pjsip_100rel_attach(pjsip_inv_session * inv);
//extern void pjsip_dlg_dec_lock(pjsip_dialog * dlg);
//extern void pjsip_dlg_inc_lock(pjsip_dialog * dlg);
//extern pj_status_t pjsip_dlg_inc_session(pjsip_dialog * dlg,pjsip_module * mod);
//extern pjsip_transaction * pjsip_rdata_get_tsx(pjsip_rx_data * rdata);
//extern pj_pool_t * pjsip_endpt_create_pool(pjsip_endpoint * endpt,const char * pool_name,pj_size_t initial,pj_size_t increment);
//extern pj_status_t pjmedia_sdp_neg_create_w_remote_offer(pj_pool_t * pool,const pjmedia_sdp_session * initial,const pjmedia_sdp_session * remote,pjmedia_sdp_neg ** p_neg);
//extern pj_status_t pjmedia_sdp_validate(const pjmedia_sdp_session * sdp);
//extern pj_status_t pjmedia_sdp_neg_create_w_local_offer(pj_pool_t * pool,const pjmedia_sdp_session * local,pjmedia_sdp_neg ** p_neg);
//extern pj_status_t pjsip_dlg_add_usage(pjsip_dialog * dlg,pjsip_module * module,void * mod_data);
//extern pj_status_t pjmedia_sdp_parse(pj_pool_t * pool,char * buf,pj_size_t len,pjmedia_sdp_session ** p_sdp);

// the following function fuzzes pjmedia_sdp_parse based on the above API usages
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
// First, we need to initialize pjproject
	pj_status_t status;

	pj_caching_pool cp;
	pjmedia_sdp_session *local_sdp = NULL;
	pj_bzero(&cp, sizeof(cp));
	status = pj_init();
	if (status != PJ_SUCCESS) {
		return 0;
	}
	pj_caching_pool_init(&cp, NULL, 0);

// Then, we need to allocate some memory for the SDP session

	pj_pool_t *pool = pj_pool_create(&cp.factory, "sample", 1000, 1000, NULL);

	char buf[Size + 1];
	pj_memcpy(buf, Data, Size);
	buf[Size] = '\0';

// Parse SDP and validate it if SDP is present in the buffer
	if (strchr((const char*)buf, 'm') != NULL && strchr((const char*)buf, 'o') != NULL) {

		pjmedia_sdp_session *remote_sdp = NULL;
		pj_status_t status = pjmedia_sdp_parse(pool, (char*)buf, strlen((char*)buf), &remote_sdp);

		if (status != PJ_SUCCESS) {
			goto end;
		}

		status = pjmedia_sdp_validate(remote_sdp);
		if (status != PJ_SUCCESS) {
			goto end;
		}

// Create negotiator if remote SDP is present

		if (remote_sdp) {
			status = pjmedia_sdp_neg_create_w_remote_offer(pool, local_sdp, remote_sdp, NULL);
		}
	}

end:
// Cleanup and return
	pj_pool_release(pool);
	pj_caching_pool_destroy(&cp);
	pj_shutdown();
	return 0;
}