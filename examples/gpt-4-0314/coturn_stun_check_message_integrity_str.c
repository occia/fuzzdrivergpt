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

// @ examples of API usage from coturn/src/apps/uclient/uclient.c-check_integrity
// int check_integrity(app_ur_conn_info *clnet_info, stun_buffer *message) {
//   SHATYPE sht = shatype;
// 
//   if (oauth && clnet_info->oauth) {
// 
//     password_t pwd;
// 
//     return stun_check_message_integrity_by_key_str(get_turn_credentials_type(), message->buf, (size_t)(message->len),
//                                                    clnet_info->key, pwd, sht);
// 
//   } else {
// 
//     if (stun_check_message_integrity_str(get_turn_credentials_type(), message->buf, (size_t)(message->len), g_uname,
//                                          clnet_info->realm, g_upwd, sht) < 1) {
//       TURN_LOG_FUNC(TURN_LOG_LEVEL_INFO, "Wrong integrity in a message received from server\n");
//       return -1;
//     }
//   }
// 
//   return 0;
// }

//extern int stun_check_message_integrity_str(turn_credential_type ct,uint8_t * buf,size_t len,const uint8_t * uname,const uint8_t * realm,const uint8_t * upwd,SHATYPE shatype);
//extern int stun_check_message_integrity_by_key_str(turn_credential_type ct,uint8_t * buf,size_t len,hmackey_t key,password_t pwd,SHATYPE shatype);

// the following function fuzzes stun_check_message_integrity_str based on the above API usages
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
if (Size < 3)
    return 0;

  turn_credential_type ct = (Data[0] % 2) + 1;
  SHATYPE shatype = (Data[1] % 3);

  uint8_t buf[1024];
  memcpy(buf, Data, Size < sizeof(buf) ? Size : sizeof(buf));
  size_t len = Size;

  uint8_t uname[] = "username";
  uint8_t realm[] = "example.org";
  uint8_t upwd[] = "password";

  // call the fuzzed function
  int ret = stun_check_message_integrity_str(ct, buf, len, uname, realm, upwd, shatype);

  return 0;
}