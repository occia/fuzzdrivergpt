#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include "igraph/igraph.h"

// ```
// #include "igraph/igraph_foreign.h"
// 
// //extern igraph_error_t igraph_read_graph_lgl(igraph_t * graph,FILE * instream,igraph_bool_t names,igraph_add_weights_t weights,igraph_bool_t directed);
// 
// // the following function fuzzes igraph_read_graph_lgl
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
// if (Size == 0) {
//     return 0;
//   }
// 
//   FILE *instream;
//   igraph_t graph;
//   igraph_bool_t names = 1;
//   igraph_add_weights_t weights = IGRAPH_ADD_WEIGHTS_IF_PRESENT;
//   igraph_bool_t directed = 1;
// 
//   // Create a temporary file to store the input data
//   instream = tmpfile();
//   if (!instream) {
//     return 0;
//   }
// 
//   // Write input data to the temporary file
//   if (fwrite(Data, 1, Size, instream) != Size) {
//     fclose(instream);
//     return 0;
//   }
// 
//   // Rewind the file to the beginning
//   rewind(instream);
// 
//   // Call the target function
//   igraph_error_t ret = igraph_read_graph_lgl(&graph, instream, names, weights, directed);
// 
//   // Destroy the graph and close the temporary file
//   if (ret == IGRAPH_SUCCESS) {
//     igraph_destroy(&graph);
//   }
//   fclose(instream);
// 
//   return 0;
// }
// ```
// 
// The above C code can be built successfully but will crash (libFuzzer-deadly signal).
// The crash line is:
// igraph_error_t ret = igraph_read_graph_lgl(&graph, instream, names, weights, directed);
// 
// The frames of the stack are:
// #0 0x5391c1 in __sanitizer_print_stack_trace /src/llvm-project/compiler-rt/lib/asan/asan_stack.cpp:87:3
// #1 0x584e95 in igraph_abort /src/igraph/src/core/error.c:69:5
// #2 0x585058 in igraph_error_handler_abort /src/igraph/src/core/error.c:202:5
// #3 0x585058 in igraph_error /src/igraph/src/core/error.c:174:9
// #4 0x577e00 in igraph_read_graph_lgl /src/igraph/src/io/lgl.c
// #5 0x56a019 in LLVMFuzzerTestOneInput /root/workspace/jarvis/targets/igraph/c/para-iter-account-7-0/dummyfuzzer.c:43:24
// 
// 
// 
// Based on the above information, fix the code.
#include "igraph/igraph_foreign.h"

//extern igraph_error_t igraph_read_graph_lgl(igraph_t * graph,FILE * instream,igraph_bool_t names,igraph_add_weights_t weights,igraph_bool_t directed);

// the following function fuzzes igraph_read_graph_lgl
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
  if (Size == 0) {
    return 0;
  }

  FILE *instream;
  igraph_t graph;
  igraph_bool_t names = 1;
  igraph_add_weights_t weights = IGRAPH_ADD_WEIGHTS_IF_PRESENT;
  igraph_bool_t directed = 1;

  // Create a temporary file to store the input data
  instream = tmpfile();
  if (!instream) {
    return 0;
  }

  // Write input data to the temporary file
  if (fwrite(Data, 1, Size, instream) != Size) {
    fclose(instream);
    return 0;
  }

  // Rewind the file to the beginning
  rewind(instream);

  // Call the target function
  igraph_set_error_handler(igraph_error_handler_ignore); // Set error handler to ignore errors instead of aborting
  igraph_error_t ret = igraph_read_graph_lgl(&graph, instream, names, weights, directed);

  // Destroy the graph and close the temporary file
  if (ret == IGRAPH_SUCCESS) {
    igraph_destroy(&graph);
  }
  fclose(instream);

  return 0;
}