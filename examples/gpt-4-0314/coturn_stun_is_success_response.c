#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>

#include <fcntl.h>

// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.

#include "turn/stun_buffer.h"

// @ examples of API usage from coturn/src/apps/stunclient/stunclient.c-run_stunclient
// static int run_stunclient(const char *rip, int rport, int *port, int *rfc5780, int response_port, int change_ip,
//                           int change_port, int padding) {
// 
//   ioa_addr remote_addr;
//   int new_udp_fd = -1;
//   stun_buffer buf;
// 
//   memset(&remote_addr, 0, sizeof(remote_addr));
//   if (make_ioa_addr((const uint8_t *)rip, rport, &remote_addr) < 0)
//     err(-1, NULL);
// 
//   if (udp_fd < 0) {
//     udp_fd = socket(remote_addr.ss.sa_family, CLIENT_DGRAM_SOCKET_TYPE, CLIENT_DGRAM_SOCKET_PROTOCOL);
//     if (udp_fd < 0)
//       err(-1, NULL);
// 
//     if (!addr_any(&real_local_addr)) {
//       if (addr_bind(udp_fd, &real_local_addr, 0, 1, UDP_SOCKET) < 0)
//         err(-1, NULL);
//     }
//   }
// 
//   if (response_port >= 0) {
// 
//     new_udp_fd = socket(remote_addr.ss.sa_family, CLIENT_DGRAM_SOCKET_TYPE, CLIENT_DGRAM_SOCKET_PROTOCOL);
//     if (new_udp_fd < 0)
//       err(-1, NULL);
// 
//     addr_set_port(&real_local_addr, response_port);
// 
//     if (addr_bind(new_udp_fd, &real_local_addr, 0, 1, UDP_SOCKET) < 0)
//       err(-1, NULL);
//   }
// 
//   stun_prepare_binding_request(&buf);
// 
//   if (response_port >= 0) {
//     stun_attr_add_response_port_str((uint8_t *)(buf.buf), (size_t *)&(buf.len), (uint16_t)response_port);
//   }
//   if (change_ip || change_port) {
//     stun_attr_add_change_request_str((uint8_t *)buf.buf, (size_t *)&(buf.len), change_ip, change_port);
//   }
//   if (padding) {
//     if (stun_attr_add_padding_str((uint8_t *)buf.buf, (size_t *)&(buf.len), 1500) < 0) {
//       printf("%s: ERROR: Cannot add padding\n", __FUNCTION__);
//     }
//   }
// 
//   {
//     int len = 0;
//     int slen = get_ioa_addr_len(&remote_addr);
// 
//     do {
//       len = sendto(udp_fd, buf.buf, buf.len, 0, (struct sockaddr *)&remote_addr, (socklen_t)slen);
//     } while (len < 0 && (socket_eintr() || socket_enobufs() || socket_eagain()));
// 
//     if (len < 0)
//       err(-1, NULL);
//   }
// 
//   if (addr_get_from_sock(udp_fd, &real_local_addr) < 0) {
//     printf("%s: Cannot get address from local socket\n", __FUNCTION__);
//   } else {
//     *port = addr_get_port(&real_local_addr);
//   }
// 
//   {
//     if (new_udp_fd >= 0) {
//       socket_closesocket(udp_fd);
//       udp_fd = new_udp_fd;
//       new_udp_fd = -1;
//     }
//   }
// 
//   {
//     int len = 0;
//     uint8_t *ptr = buf.buf;
//     int recvd = 0;
//     const int to_recv = sizeof(buf.buf);
// 
//     do {
//       len = recv(udp_fd, ptr, to_recv - recvd, 0);
//       if (len > 0) {
//         recvd += len;
//         ptr += len;
//         break;
//       }
//     } while (len < 0 && (socket_eintr() || socket_eagain()));
// 
//     if (recvd > 0)
//       len = recvd;
//     buf.len = len;
// 
//     if (stun_is_command_message(&buf)) {
// 
//       if (stun_is_response(&buf)) {
// 
//         if (stun_is_success_response(&buf)) {
// 
//           if (stun_is_binding_response(&buf)) {
// 
//             ioa_addr reflexive_addr;
//             addr_set_any(&reflexive_addr);
//             if (stun_attr_get_first_addr(&buf, STUN_ATTRIBUTE_XOR_MAPPED_ADDRESS, &reflexive_addr, NULL) >= 0) {
// 
//               stun_attr_ref sar = stun_attr_get_first_by_type_str(buf.buf, buf.len, STUN_ATTRIBUTE_OTHER_ADDRESS);
//               if (sar) {
//                 *rfc5780 = 1;
//                 printf("\n========================================\n");
//                 printf("RFC 5780 response %d\n", ++counter);
//                 ioa_addr other_addr;
//                 stun_attr_get_addr_str((uint8_t *)buf.buf, (size_t)buf.len, sar, &other_addr, NULL);
//                 sar = stun_attr_get_first_by_type_str(buf.buf, buf.len, STUN_ATTRIBUTE_RESPONSE_ORIGIN);
//                 if (sar) {
//                   ioa_addr response_origin;
//                   stun_attr_get_addr_str((uint8_t *)buf.buf, (size_t)buf.len, sar, &response_origin, NULL);
//                   addr_debug_print(1, &response_origin, "Response origin: ");
//                 }
//                 addr_debug_print(1, &other_addr, "Other addr: ");
//               }
//               addr_debug_print(1, &reflexive_addr, "UDP reflexive addr");
// 
//             } else {
//               printf("Cannot read the response\n");
//             }
//           } else {
//             printf("Wrong type of response\n");
//           }
//         } else {
//           int err_code = 0;
//           uint8_t err_msg[1025] = "\0";
//           size_t err_msg_size = sizeof(err_msg);
//           if (stun_is_error_response(&buf, &err_code, err_msg, err_msg_size)) {
//             printf("The response is an error %d (%s)\n", err_code, (char *)err_msg);
//           } else {
//             printf("The response is an unrecognized error\n");
//           }
//         }
//       } else {
//         printf("The response is not a response message\n");
//       }
//     } else {
//       printf("The response is not a STUN message\n");
//     }
//   }
// 
//   return 0;
// }

//extern int addr_get_port(const ioa_addr * addr);
//extern int stun_attr_add_response_port_str(uint8_t * buf,size_t * len,uint16_t port);
//extern int stun_is_response(const stun_buffer * buf);
//extern int addr_any(const ioa_addr * addr);
//extern int stun_attr_add_padding_str(uint8_t * buf,size_t * len,uint16_t padding_len);
//extern int stun_attr_get_addr_str(const uint8_t * buf,size_t len,stun_attr_ref attr,ioa_addr * ca,const ioa_addr * default_addr);
//extern int make_ioa_addr(const uint8_t * saddr,int port,ioa_addr * addr);
//extern stun_attr_ref stun_attr_get_first_by_type_str(const uint8_t * buf,size_t len,uint16_t attr_type);
//extern int stun_attr_get_first_addr(const stun_buffer * buf,uint16_t attr_type,ioa_addr * ca,const ioa_addr * default_addr);
//extern int stun_is_command_message(const stun_buffer * buf);
//extern int stun_is_success_response(const stun_buffer * buf);
//extern int addr_bind(int fd,const ioa_addr * addr,int reusable,int debug,SOCKET_TYPE st);
//extern int addr_get_from_sock(int fd,ioa_addr * addr);
//extern void stun_prepare_binding_request(stun_buffer * buf);
//extern uint32_t get_ioa_addr_len(const ioa_addr * addr);
//extern int stun_is_binding_response(const stun_buffer * buf);
//extern void addr_set_port(ioa_addr * addr,int port);
//extern void addr_debug_print(int verbose,const ioa_addr * addr,const char * s);
//extern int stun_attr_add_change_request_str(uint8_t * buf,size_t * len,int change_ip,int change_port);
//extern void addr_set_any(ioa_addr * addr);
//extern int stun_is_error_response(const stun_buffer * buf,int * err_code,uint8_t * err_msg,size_t err_msg_size);

// the following function fuzzes stun_is_success_response based on the above API usages
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
ioa_addr remote_addr;
  ioa_addr real_local_addr;
  ioa_addr reflexive_addr;
  int udp_fd = -1;
  stun_buffer buf;

  if (Size < 4) {
    return 0;
  }

  uint8_t padding_len = Data[0];
  uint16_t response_port = (Data[1] << 8) | Data[2];
  uint16_t rport = (Data[3] << 8) | Data[4];
  Data += 4;
  Size -= 4;

  memset(&buf, 0, sizeof(buf));
  memcpy(buf.buf, Data, Size);
  buf.len = Size;

  if (!stun_is_command_message(&buf)) {
    return 0;
  }

  // Prepare binding request
  stun_prepare_binding_request(&buf);

  if (response_port >= 0) {
    stun_attr_add_response_port_str((uint8_t *)(buf.buf), (size_t *)&(buf.len), (uint16_t)response_port);
  }

  // Add padding_str
  if (stun_attr_add_padding_str((uint8_t *)(buf.buf), (size_t *)&(buf.len), padding_len) < 0) {
    return 0;
  }

  // Run stun_is_success_response
  int success = stun_is_success_response(&buf);
  if (success) {
    if (stun_is_binding_response(&buf)) {
      addr_set_any(&reflexive_addr);
      if (stun_attr_get_first_addr(&buf, STUN_ATTRIBUTE_XOR_MAPPED_ADDRESS, &reflexive_addr, NULL) >= 0) {
        addr_debug_print(1, &reflexive_addr, "UDP reflexive addr");
      }
    }
  } else {
    int err_code = 0;
    uint8_t err_msg[1025] = "\0";
    size_t err_msg_size = sizeof(err_msg);
    if (stun_is_error_response(&buf, &err_code, err_msg, err_msg_size)) {
    } else {
    }
  }

  return 0;
}