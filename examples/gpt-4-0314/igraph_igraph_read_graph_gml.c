#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include "igraph/igraph.h"

// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.

#include "igraph/igraph_foreign.h"

//extern igraph_error_t igraph_read_graph_gml(igraph_t * graph,FILE * instream);

// the following function fuzzes igraph_read_graph_gml
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
if (Size == 0) {
    return 0;
  }

  FILE *InStream = fmemopen((void *)Data, Size, "rb");
  if (!InStream) {
    return 0;
  }

  igraph_t graph;
  igraph_empty(&graph, 0, IGRAPH_UNDIRECTED);

  igraph_error_handler_t *old_handler = igraph_set_error_handler(igraph_error_handler_ignore);
  igraph_warning_handler_t *old_warning_handler = igraph_set_warning_handler(igraph_warning_handler_ignore);

  igraph_read_graph_gml(&graph, InStream);

  igraph_destroy(&graph);
  fclose(InStream);

  igraph_set_error_handler(old_handler);
  igraph_set_warning_handler(old_warning_handler);

  return 0;
}