#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include "igraph/igraph.h"

// ```
// #include "igraph/igraph_separators.h"
// 
// //extern igraph_error_t igraph_all_minimal_st_separators(const igraph_t * graph,igraph_vector_int_list_t * separators);
// 
// // the following function fuzzes igraph_all_minimal_st_separators
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//     // Ensure that Size is at least 2
//     if (Size < 2) {
//         return 0;
//     }
// 
//     // Ensure that Size is even
//     if (Size % 2 != 0) {
//         Size--; // ignore the last byte
//     }
// 
//     // First, we need to create an igraph_t object from the input data.
//     igraph_t graph;
//     igraph_empty(&graph, 0, IGRAPH_DIRECTED);
// 
//     // Populate the graph with edges
//     for (size_t i = 0; i < Size; i += 2) {
//         igraph_integer_t from = Data[i];
//         igraph_integer_t to = Data[i + 1];
//         if(from >=0 && to>=0){ // check if the vertex IDs are non-negative
//             igraph_add_edge(&graph, from, to);
//         }
//     }
// 
//     // Create a vector to hold the separators
//     igraph_vector_int_list_t separators;
//     igraph_vector_int_list_init(&separators, 10);
// 
//     // Call the function we want to fuzz
//     igraph_all_minimal_st_separators(&graph, &separators);
// 
//     // Clean up the memory used by the igraph_t object and the vector of separators
//     igraph_destroy(&graph);
//     igraph_vector_int_list_destroy(&separators);
// 
//     // Return 0 to indicate that the function was executed without errors
//     return 0;
// }
// ```
// 
// The above C code can be built successfully but will crash (libFuzzer-deadly signal).
// The crash line is:
// igraph_add_edge(&graph, from, to);
// 
// The frames of the stack are:
// #0 0x5391c1 in __sanitizer_print_stack_trace /src/llvm-project/compiler-rt/lib/asan/asan_stack.cpp:87:3
// #1 0x5b9b85 in igraph_abort /src/igraph/src/core/error.c:69:5
// #2 0x5b9d48 in igraph_error_handler_abort /src/igraph/src/core/error.c:202:5
// #3 0x5b9d48 in igraph_error /src/igraph/src/core/error.c:174:9
// #4 0x572f33 in igraph_add_edges /src/igraph/src/graph/type_indexededgelist.c:261:9
// #5 0x59d2df in igraph_add_edge /src/igraph/src/operators/add_edge.c:58:5
// #6 0x56a073 in LLVMFuzzerTestOneInput /root/workspace/jarvis/targets/igraph/c/para-iter-account-6-0/dummyfuzzer.c:96:13
// 
// 
// 
// Based on the above information, fix the code.
#include "igraph/igraph_separators.h"

//extern igraph_error_t igraph_all_minimal_st_separators(const igraph_t * graph,igraph_vector_int_list_t * separators);

// the following function fuzzes igraph_all_minimal_st_separators
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    // Ensure that Size is at least 2
    if (Size < 2) {
        return 0;
    }

    // Ensure that Size is even
    if (Size % 2 != 0) {
        Size--; // ignore the last byte
    }

    // First, we need to create an igraph_t object from the input data.
    igraph_t graph;
    igraph_empty(&graph, 0, IGRAPH_DIRECTED);

    // Populate the graph with edges
    for (size_t i = 0; i < Size; i += 2) {
        igraph_integer_t from = Data[i];
        igraph_integer_t to = Data[i + 1];
        if(from >= 0 && to >= 0 && from < igraph_vcount(&graph) && to < igraph_vcount(&graph)){ // check if the vertex IDs are non-negative and within bounds
            igraph_add_edge(&graph, from, to);
        }
    }

    // Create a vector to hold the separators
    igraph_vector_int_list_t separators;
    igraph_vector_int_list_init(&separators, 10);

    // Call the function we want to fuzz
    igraph_all_minimal_st_separators(&graph, &separators);

    // Clean up the memory used by the igraph_t object and the vector of separators
    igraph_destroy(&graph);
    igraph_vector_int_list_destroy(&separators);

    // Return 0 to indicate that the function was executed without errors
    return 0;
}