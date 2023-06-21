#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>

#include <fcntl.h>

// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.

#include "turn/client/ns_turn_msg.h"

// @ examples of API usage from dep/coturn/src/server/ns_turn_server.c-read_client_connection
// static int read_client_connection(turn_turnserver *server, ts_ur_session *elem,
// 				  	  	  	  	  ts_ur_super_session *ss, ioa_net_data *in_buffer,
// 				  	  	  	  	  int can_resume, int count_usage) {
// 
// 	FUNCSTART;
// 
// 	if (!server || !elem || !ss || !in_buffer) {
// 		FUNCEND;
// 		return -1;
// 	}
// 
// 	if (elem->state != UR_STATE_READY) {
// 		FUNCEND;
// 		return -1;
// 	}
// 
// 	int ret = (int)ioa_network_buffer_get_size(in_buffer->nbh);
// 	if (ret < 0) {
// 		FUNCEND;
// 		return -1;
// 	}
// 
// 	if(count_usage) {
// 		++(ss->received_packets);
// 		ss->received_bytes += (u32bits)ioa_network_buffer_get_size(in_buffer->nbh);
// 		turn_report_session_usage(ss);
// 	}
// 
// 	if (eve(server->verbose)) {
// 		TURN_LOG_FUNC(TURN_LOG_LEVEL_INFO,
// 			      "%s: data.buffer=0x%lx, data.len=%ld\n", __FUNCTION__,
// 			      (long)ioa_network_buffer_data(in_buffer->nbh), 
// 			      (long)ioa_network_buffer_get_size(in_buffer->nbh));
// 	}
// 
// 	u16bits chnum = 0;
// 	u32bits old_stun_cookie = 0;
// 
// 	size_t blen = ioa_network_buffer_get_size(in_buffer->nbh);
// 	size_t orig_blen = blen;
// 	SOCKET_TYPE st = get_ioa_socket_type(ss->client_session.s);
// 	int is_padding_mandatory = ((st == TCP_SOCKET)||(st==TLS_SOCKET)||(st==TENTATIVE_TCP_SOCKET));
// 
// 	if (stun_is_channel_message_str(ioa_network_buffer_data(in_buffer->nbh), 
// 					&blen,
// 					&chnum,
// 					is_padding_mandatory)) {
// 
// 		if(ss->is_tcp_relay) {
// 			//Forbidden
// 			FUNCEND;
// 			return -1;
// 		}
// 
// 		int rc = 0;
// 
// 		if(blen<=orig_blen) {
// 			ioa_network_buffer_set_size(in_buffer->nbh,blen);
// 			rc = write_to_peerchannel(ss, chnum, in_buffer);
// 		}
// 
// 		if (eve(server->verbose)) {
// 			TURN_LOG_FUNC(TURN_LOG_LEVEL_INFO, "%s: wrote to peer %d bytes\n",
// 					__FUNCTION__, (int) rc);
// 		}
// 
// 		FUNCEND;
// 		return 0;
// 
// 	} else if (stun_is_command_message_full_check_str(ioa_network_buffer_data(in_buffer->nbh), ioa_network_buffer_get_size(in_buffer->nbh), 0, &(ss->enforce_fingerprints))) {
// 
// 		ioa_network_buffer_handle nbh = ioa_network_buffer_allocate(server->e);
// 		int resp_constructed = 0;
// 
// 		u16bits method = stun_get_method_str(ioa_network_buffer_data(in_buffer->nbh),
// 						ioa_network_buffer_get_size(in_buffer->nbh));
// 
// 		handle_turn_command(server, ss, in_buffer, nbh, &resp_constructed, can_resume);
// 
// 		if((method != STUN_METHOD_BINDING) && (method != STUN_METHOD_SEND))
// 			report_turn_session_info(server,ss,0);
// 
// 		if(ss->to_be_closed || ioa_socket_tobeclosed(ss->client_session.s)) {
// 			FUNCEND;
// 			ioa_network_buffer_delete(server->e, nbh);
// 			return 0;
// 		}
// 
// 		if (resp_constructed) {
// 
// 			if ((server->fingerprint) || ss->enforce_fingerprints) {
// 				size_t len = ioa_network_buffer_get_size(nbh);
// 				if (stun_attr_add_fingerprint_str(ioa_network_buffer_data(nbh), &len) < 0) {
// 					FUNCEND	;
// 					ioa_network_buffer_delete(server->e, nbh);
// 					return -1;
// 				}
// 				ioa_network_buffer_set_size(nbh, len);
// 			}
// 
// 			int ret = write_client_connection(server, ss, nbh, TTL_IGNORE, TOS_IGNORE);
// 
// 			FUNCEND	;
// 			return ret;
// 		} else {
// 			ioa_network_buffer_delete(server->e, nbh);
// 			return 0;
// 		}
// 
// 	} else if (old_stun_is_command_message_str(ioa_network_buffer_data(in_buffer->nbh), ioa_network_buffer_get_size(in_buffer->nbh), &old_stun_cookie) && !(*(server->no_stun))) {
// 
// 		ioa_network_buffer_handle nbh = ioa_network_buffer_allocate(server->e);
// 		int resp_constructed = 0;
// 
// 		handle_old_stun_command(server, ss, in_buffer, nbh, &resp_constructed, old_stun_cookie);
// 
// 		if (resp_constructed) {
// 
// 			int ret = write_client_connection(server, ss, nbh, TTL_IGNORE, TOS_IGNORE);
// 
// 			FUNCEND	;
// 			return ret;
// 		} else {
// 			ioa_network_buffer_delete(server->e, nbh);
// 			return 0;
// 		}
// 
// 	} else {
// 		SOCKET_TYPE st = get_ioa_socket_type(ss->client_session.s);
// 		if((st == TCP_SOCKET)||(st==TLS_SOCKET)||(st==TENTATIVE_TCP_SOCKET)) {
// 			if(is_http_get((char*)ioa_network_buffer_data(in_buffer->nbh), ioa_network_buffer_get_size(in_buffer->nbh)))
// 				write_http_echo(server,ss);
// 		}
// 	}
// 
// 	//Unrecognized message received, ignore it
// 
// 	FUNCEND;
// 	return -1;
// }

//extern int stun_attr_add_fingerprint_str(uint8_t * buf,size_t * len);
//extern SOCKET_TYPE get_ioa_socket_type(ioa_socket_handle s);
//extern void ioa_network_buffer_delete(ioa_engine_handle e,ioa_network_buffer_handle nbh);
//extern ioa_network_buffer_handle ioa_network_buffer_allocate(ioa_engine_handle e);
//extern int report_turn_session_info(turn_turnserver * server,ts_ur_super_session * ss,int force_invalid);
//extern int old_stun_is_command_message_str(const uint8_t * buf,size_t blen,uint32_t * cookie);
//extern uint8_t * ioa_network_buffer_data(ioa_network_buffer_handle nbh);
//extern int ioa_socket_tobeclosed(ioa_socket_handle s);
//extern void ioa_network_buffer_set_size(ioa_network_buffer_handle nbh,size_t len);
//extern int stun_is_command_message_full_check_str(const uint8_t * buf,size_t blen,int must_check_fingerprint,int * fingerprint_present);
//extern int stun_is_channel_message_str(const uint8_t * buf,size_t * blen,uint16_t * chnumber,int mandatory_padding);
//extern uint16_t stun_get_method_str(const uint8_t * buf,size_t len);
//extern size_t ioa_network_buffer_get_size(ioa_network_buffer_handle nbh);
//extern void turn_report_session_usage(void * session,int force_invalid);

// the following function fuzzes stun_is_command_message_full_check_str based on the above API usages
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
// Complete the implementation of the fuzz driver:

    uint8_t *buf = (uint8_t *)Data;
    size_t blen = Size;
    int must_check_fingerprint = 0;
    int fingerprint_present = 0;

    stun_is_command_message_full_check_str(buf, blen, must_check_fingerprint, &fingerprint_present);

    return 0;
}