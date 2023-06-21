#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>

#include "igraph/igraph.h"

// ```
// #include "igraph/igraph_foreign.h"
// 
// // the following function fuzzes igraph_read_graph_lgl
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//     // First, we need to check if the input data is large enough to contain at least one valid LGL graph. If not, we return early.
//     if (Size < 20) {
//         return 0;
//     }
// 
//     // Allocate a new igraph object.
//     igraph_t graph;
//     igraph_empty(&graph, 1, IGRAPH_UNDIRECTED);
//     if (igraph_vcount(&graph) == 0) {
//         igraph_destroy(&graph);
//         return 0;
//     }
// 
//     // Open a temporary file for writing the input data to.
//     FILE* tmp_file = tmpfile();
//     if (!tmp_file) {
//         igraph_destroy(&graph);
//         return 0;
//     }
// 
//     // Write the input data to the temporary file.
//     if (fwrite(Data, sizeof(uint8_t), Size, tmp_file) != Size) {
//         fclose(tmp_file);
//         igraph_destroy(&graph);
//         return 0;
//     }
// 
//     // Call igraph_read_graph_lgl to read the graph from the temporary file.
//     igraph_error_t err = igraph_read_graph_lgl(&graph, tmp_file, 0, IGRAPH_ADD_WEIGHTS_NO, 1);
// 
//     // Close and remove the temporary file.
//     fclose(tmp_file);
// 
//     if (err != IGRAPH_SUCCESS) {
//         igraph_destroy(&graph);
//         return 0;
//     }
// 
//     // Destroy the igraph object.
//     igraph_destroy(&graph);
// 
//     // Return 0 if there was no error, or a nonzero value if there was an error.
//     return 0;
// }
// ```
// 
// The above C code can be built successfully but has runtime memory leak.
// The leak related lines of code are:
//     igraph_empty(&graph, 1, IGRAPH_UNDIRECTED);
//     igraph_empty(&graph, 1, IGRAPH_UNDIRECTED);
//     igraph_empty(&graph, 1, IGRAPH_UNDIRECTED);
// 
// Based on the above information, fix the code.
#include "igraph/igraph_foreign.h"

// the following function fuzzes igraph_read_graph_lgl
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    // First, we need to check if the input data is large enough to contain at least one valid LGL graph. If not, we return early.
    if (Size < 20) {
        return 0;
    }

    // Allocate a new igraph object.
    igraph_t graph;
    igraph_empty(&graph, 1, IGRAPH_UNDIRECTED);
    igraph_destroy(&graph);

    // Allocate a new igraph object.
    igraph_empty(&graph, 1, IGRAPH_UNDIRECTED);
    igraph_destroy(&graph);

    // Allocate a new igraph object.
    igraph_empty(&graph, 1, IGRAPH_UNDIRECTED);
    igraph_destroy(&graph);

    // Open a temporary file for writing the input data to.
    FILE* tmp_file = tmpfile();
    if (!tmp_file) {
        return 0;
    }

    // Write the input data to the temporary file.
    if (fwrite(Data, sizeof(uint8_t), Size, tmp_file) != Size) {
        fclose(tmp_file);
        return 0;
    }

    // Call igraph_read_graph_lgl to read the graph from the temporary file.
    igraph_error_t err = igraph_read_graph_lgl(&graph, tmp_file, 0, IGRAPH_ADD_WEIGHTS_NO, 1);

    // Close and remove the temporary file.
    fclose(tmp_file);

    if (err != IGRAPH_SUCCESS) {
        return 0;
    }

    // Destroy the igraph object.
    igraph_destroy(&graph);

    // Return 0 if there was no error, or a nonzero value if there was an error.
    return 0;
}