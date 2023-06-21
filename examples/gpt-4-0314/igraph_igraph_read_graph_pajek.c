#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include "igraph/igraph.h"

// ```
// #include "igraph/igraph_foreign.h"
// 
// //extern igraph_error_t igraph_read_graph_pajek(igraph_t * graph,FILE * instream);
// 
// // the following function fuzzes igraph_read_graph_pajek
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//   // Wrap the data in a memory stream
//   FILE *instream = fmemopen((void *)Data, Size, "rb");
//   if (!instream) {
//     return 0;
//   }
// 
//   // Create an empty graph
//   igraph_t graph;
//   igraph_empty(&graph, 0, IGRAPH_UNDIRECTED);
// 
//   // Set up error handling
//   igraph_set_error_handler(igraph_error_handler_ignore);
// 
//   // Call the function to fuzz
//   igraph_error_t result = igraph_read_graph_pajek(&graph, instream);
// 
//   // Close the input stream
//   fclose(instream);
// 
//   // Check for errors and destroy the graph only if it has been successfully created
//   if (result == IGRAPH_SUCCESS) {
//     igraph_destroy(&graph);
//   }
// 
//   // Reset error handling to default behavior
//   igraph_set_error_handler(igraph_error_handler_abort);
// 
//   return 0;
// }
// ```
// 
// The above C code can be built successfully but meet out-of-memory, perhaps due to memory leak.
// The out-of-memory related stacks are:
//   igraph_empty(&graph, 0, IGRAPH_UNDIRECTED);
//   igraph_empty(&graph, 0, IGRAPH_UNDIRECTED);
// 
// Based on the above information, fix the code.
#include "igraph/igraph_foreign.h"

//extern igraph_error_t igraph_read_graph_pajek(igraph_t * graph,FILE * instream);

// the following function fuzzes igraph_read_graph_pajek
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
  // Wrap the data in a memory stream
  FILE *instream = fmemopen((void *)Data, Size, "rb");
  if (!instream) {
    return 0;
  }

  // Create an empty graph
  igraph_t graph;
  igraph_empty(&graph, 0, IGRAPH_UNDIRECTED);

  // Set up error handling
  igraph_set_error_handler(igraph_error_handler_ignore);

  // Call the function to fuzz
  igraph_error_t result = igraph_read_graph_pajek(&graph, instream);

  // Close the input stream
  fclose(instream);

  // Destroy the graph regardless of success or failure
  igraph_destroy(&graph);

  // Reset error handling to default behavior
  igraph_set_error_handler(igraph_error_handler_abort);

  return 0;
}