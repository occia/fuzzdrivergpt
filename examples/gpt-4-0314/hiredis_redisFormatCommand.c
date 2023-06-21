#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>


// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.

#include "hiredis/hiredis.h"

// @ examples of API usage from discnt-benchmark.c-createClient
// static client createClient(char *cmd, size_t len, client from) {
//     int j;
//     client c = zmalloc(sizeof(struct _client));
// 
//     if (config.hostsocket == NULL) {
//         c->context = redisConnectNonBlock(config.hostip,config.hostport);
//     } else {
//         c->context = redisConnectUnixNonBlock(config.hostsocket);
//     }
//     if (c->context->err) {
//         fprintf(stderr,"Could not connect to Discnt at ");
//         if (config.hostsocket == NULL)
//             fprintf(stderr,"%s:%d: %s\n",config.hostip,config.hostport,c->context->errstr);
//         else
//             fprintf(stderr,"%s: %s\n",config.hostsocket,c->context->errstr);
//         exit(1);
//     }
//     /* Suppress hiredis cleanup of unused buffers for max speed. */
//     c->context->reader->maxbuf = 0;
// 
//     /* Build the request buffer:
//      * Queue N requests accordingly to the pipeline size, or simply clone
//      * the example client buffer. */
//     c->obuf = sdsempty();
//     /* Prefix the request buffer with AUTH and/or SELECT commands, if applicable.
//      * These commands are discarded after the first response, so if the client is
//      * reused the commands will not be used again. */
//     c->prefix_pending = 0;
//     if (config.auth) {
//         char *buf = NULL;
//         int len = redisFormatCommand(&buf, "AUTH %s", config.auth);
//         c->obuf = sdscatlen(c->obuf, buf, len);
//         free(buf);
//         c->prefix_pending++;
//     }
// 
//     /* If a DB number different than zero is selected, prefix our request
//      * buffer with the SELECT command, that will be discarded the first
//      * time the replies are received, so if the client is reused the
//      * SELECT command will not be used again. */
//     if (config.dbnum != 0) {
//         c->obuf = sdscatprintf(c->obuf,"*2\r\n$6\r\nSELECT\r\n$%d\r\n%s\r\n",
//             (int)sdslen(config.dbnumstr),config.dbnumstr);
//         c->prefix_pending++;
//     }
//     c->prefixlen = sdslen(c->obuf);
//     /* Append the request itself. */
//     if (from) {
//         c->obuf = sdscatlen(c->obuf,
//             from->obuf+from->prefixlen,
//             sdslen(from->obuf)-from->prefixlen);
//     } else {
//         for (j = 0; j < config.pipeline; j++)
//             c->obuf = sdscatlen(c->obuf,cmd,len);
//     }
// 
//     c->written = 0;
//     c->pending = config.pipeline+c->prefix_pending;
//     c->randptr = NULL;
//     c->randlen = 0;
// 
//     /* Find substrings in the output buffer that need to be randomized. */
//     if (config.randomkeys) {
//         if (from) {
//             c->randlen = from->randlen;
//             c->randfree = 0;
//             c->randptr = zmalloc(sizeof(char*)*c->randlen);
//             /* copy the offsets. */
//             for (j = 0; j < (int)c->randlen; j++) {
//                 c->randptr[j] = c->obuf + (from->randptr[j]-from->obuf);
//                 /* Adjust for the different select prefix length. */
//                 c->randptr[j] += c->prefixlen - from->prefixlen;
//             }
//         } else {
//             char *p = c->obuf;
// 
//             c->randlen = 0;
//             c->randfree = RANDPTR_INITIAL_SIZE;
//             c->randptr = zmalloc(sizeof(char*)*c->randfree);
//             while ((p = strstr(p,"__rand_int__")) != NULL) {
//                 if (c->randfree == 0) {
//                     c->randptr = zrealloc(c->randptr,sizeof(char*)*c->randlen*2);
//                     c->randfree += c->randlen;
//                 }
//                 c->randptr[c->randlen++] = p;
//                 c->randfree--;
//                 p += 12; /* 12 is strlen("__rand_int__). */
//             }
//         }
//     }
//     if (config.idlemode == 0)
//         aeCreateFileEvent(config.el,c->context->fd,AE_WRITABLE,writeHandler,c);
//     listAddNodeTail(config.clients,c);
//     config.liveclients++;
//     return c;
// }

//extern sds sdscatprintf(sds s,const char * fmt);
//extern redisContext * redisConnectUnixNonBlock(const char * path);
//extern sds sdscatlen(sds s,const void * t,size_t len);
//extern redisContext * redisConnectNonBlock(const char * ip,int port);
//extern int redisFormatCommand(char ** target,const char * format);
//extern size_t sdslen(const sds s);

// the following function fuzzes redisFormatCommand based on the above API usages
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
char *buf = NULL;
    char *cmd;
    int len;

    if (Size == 0)
        return 0;

    cmd = malloc(Size + 1);
    memcpy(cmd, Data, Size);
    cmd[Size] = '\0';

    len = redisFormatCommand(&buf, "%s", cmd);
    if (len > 0) {
        sds s = sdsempty();
        s = sdscatlen(s, buf, len);
        free(buf);
        size_t slen = sdslen(s);
        sdsfree(s);
    }

    free(cmd);
    return 0;
}