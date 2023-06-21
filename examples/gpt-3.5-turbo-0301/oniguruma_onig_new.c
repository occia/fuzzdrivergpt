#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>

#include "oniguruma.h"
#include "oniggnu.h"

// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.

#include "oniguruma.h"

// @ examples of API usage from base.c-exec
// static int
// exec(OnigEncoding enc, OnigOptionType options, OnigSyntaxType* syntax,
//      char* apattern, char* apattern_end, char* astr, UChar* end)
// {
//   int r;
//   regex_t* reg;
//   OnigErrorInfo einfo;
//   UChar* pattern = (UChar* )apattern;
//   UChar* str     = (UChar* )astr;
//   UChar* pattern_end = (UChar* )apattern_end;
// 
//   EXEC_COUNT++;
//   EXEC_COUNT_INTERVAL++;
// 
//   onig_initialize(&enc, 1);
//   onig_set_retry_limit_in_search(RETRY_LIMIT);
// #ifdef PARSE_DEPTH_LIMIT
//   onig_set_parse_depth_limit(PARSE_DEPTH_LIMIT);
// #endif
// 
//   r = onig_new(&reg, pattern, pattern_end,
//                options, enc, syntax, &einfo);
//   if (r != ONIG_NORMAL) {
//     char s[ONIG_MAX_ERROR_MESSAGE_LEN];
//     onig_error_code_to_str((UChar* )s, r, &einfo);
// #ifdef STANDALONE
//     fprintf(stdout, "ERROR: %s\n", s);
// #endif
//     onig_end();
// 
//     if (r == ONIGERR_PARSER_BUG ||
//         r == ONIGERR_STACK_BUG  ||
//         r == ONIGERR_UNDEFINED_BYTECODE ||
//         r == ONIGERR_UNEXPECTED_BYTECODE) {
//       return -2;
//     }
//     else
//       return -1;
//   }
//   REGEX_SUCCESS_COUNT++;
// 
//   r = search(reg, pattern, pattern_end);
//   if (r == -2) return -2;
// 
//   if (onigenc_is_valid_mbc_string(enc, str, end) != 0) {
//     VALID_STRING_COUNT++;
//     r = search(reg, str, end);
//     if (r == -2) return -2;
//   }
// 
//   onig_free(reg);
//   onig_end();
//   return 0;
// }

//extern int onigenc_is_valid_mbc_string(OnigEncoding enc,const OnigUChar * s,const OnigUChar * end);
//extern void onig_free(OnigRegex );
//extern int onig_set_parse_depth_limit(unsigned int depth);
//extern int onig_initialize(OnigEncoding[] encodings,int number_of_encodings);
//extern int onig_set_retry_limit_in_search(unsigned long n);
//extern int onig_error_code_to_str(OnigUChar * s,int err_code);
//extern int onig_new(OnigRegex * ,const OnigUChar * pattern,const OnigUChar * pattern_end,OnigOptionType option,OnigEncoding enc,OnigSyntaxType * syntax,OnigErrorInfo * einfo);

// the following function fuzzes onig_new based on the above API usages
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
// first, we check if the input data is empty or smaller than the required minimum size
  if (Size < 2)
    return 0;

  // define variables to be used
  OnigEncoding encodings[1];
  OnigOptionType options = ONIG_OPTION_NONE;
  OnigSyntaxType syntax;
  OnigErrorInfo einfo;
  OnigRegex reg;
  const OnigUChar *pattern = (const OnigUChar *)Data;
  const OnigUChar *pattern_end = (const OnigUChar *)(Data + Size - 1);
  
  // initialize encoding and syntax
  encodings[0] = ONIG_ENCODING_UTF8;
  onig_initialize(encodings, 1);
  onig_set_retry_limit_in_search(5000);

  // set parse depth limit
  onig_set_parse_depth_limit(10000);

  // create new regex
  int r = onig_new(&reg, pattern, pattern_end, options, ONIG_ENCODING_UTF8, &syntax, &einfo);

  // free regex and de-initialize
  onig_free(reg);
  onig_end();

  return 0;
}