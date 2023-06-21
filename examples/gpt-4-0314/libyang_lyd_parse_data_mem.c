#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include "libyang/config.h"
#include "libyang/context.h"
#include "libyang/dict.h"
#include "libyang/in.h"
#include "libyang/libyang.h"
#include "libyang/log.h"
#include "libyang/metadata.h"
#include "libyang/out.h"
#include "libyang/parser_data.h"
#include "libyang/parser_schema.h"
#include "libyang/plugins.h"
#include "libyang/plugins_exts.h"
#include "libyang/plugins_types.h"
#include "libyang/printer_data.h"
#include "libyang/printer_schema.h"
#include "libyang/set.h"
#include "libyang/tree.h"
#include "libyang/tree_data.h"
#include "libyang/tree_edit.h"
#include "libyang/tree_schema.h"
#include "libyang/version.h"

// ```
// #include "libyang/parser_data.h"
// 
// // the following function fuzzes lyd_parse_data_mem
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//   if (Size == 0) {
//     return 0;
//   }
// 
//   const char *search_dir = NULL;
//   LY_ERR err;
//   struct ly_ctx *ctx;
// 
//   // Update the function call to take only three arguments
//   err = ly_ctx_new(search_dir, 0, &ctx);
//   if (err != LY_SUCCESS) {
//     return 0;
//   }
// 
//   // Null-terminate the input data
//   uint8_t *null_terminated_data = (uint8_t *)malloc(Size + 1);
//   if (!null_terminated_data) {
//     ly_ctx_destroy(ctx);
//     return 0;
//   }
//   memcpy(null_terminated_data, Data, Size);
//   null_terminated_data[Size] = '\0';
// 
//   struct lyd_node *tree = NULL;
// 
//   // Call the function under test with various formats and options
//   for (LYD_FORMAT format = 0; format < LYD_FORMAT_COUNT; ++format) {
//     uint32_t parse_options = 0;
//     uint32_t validate_options = 0;
//     lyd_parse_data_mem(ctx, (const char *)null_terminated_data, format, parse_options, validate_options, &tree);
// 
//     if (tree) {
//       lyd_free_tree(tree);
//       tree = NULL;
//     }
//   }
// 
//   free(null_terminated_data);
//   ly_ctx_destroy(ctx);
// 
//   return 0;
// }
// ```
// 
// The above C code has compilation error.
// The error line is:
// for (LYD_FORMAT format = 0; format < LYD_FORMAT_COUNT; ++format) {
// 
// The error description is:
// use of undeclared identifier 'LYD_FORMAT_COUNT'
// 
// Based on the above information, fix the code.
#include "libyang/parser_data.h"

// the following function fuzzes lyd_parse_data_mem
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
  if (Size == 0) {
    return 0;
  }

  const char *search_dir = NULL;
  LY_ERR err;
  struct ly_ctx *ctx;

  // Update the function call to take only three arguments
  err = ly_ctx_new(search_dir, 0, &ctx);
  if (err != LY_SUCCESS) {
    return 0;
  }

  // Null-terminate the input data
  uint8_t *null_terminated_data = (uint8_t *)malloc(Size + 1);
  if (!null_terminated_data) {
    ly_ctx_destroy(ctx);
    return 0;
  }
  memcpy(null_terminated_data, Data, Size);
  null_terminated_data[Size] = '\0';

  struct lyd_node *tree = NULL;

  // Call the function under test with various formats and options
  for (LYD_FORMAT format = 0; format < LYD_UNKNOWN; ++format) {
    uint32_t parse_options = 0;
    uint32_t validate_options = 0;
    lyd_parse_data_mem(ctx, (const char *)null_terminated_data, format, parse_options, validate_options, &tree);

    if (tree) {
      lyd_free_tree(tree);
      tree = NULL;
    }
  }

  free(null_terminated_data);
  ly_ctx_destroy(ctx);

  return 0;
}