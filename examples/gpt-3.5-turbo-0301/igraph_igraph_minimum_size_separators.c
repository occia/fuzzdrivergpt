#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>

#include "igraph/igraph.h"

// ```
// #include "igraph/igraph_separators.h"
// 
// //extern igraph_error_t igraph_minimum_size_separators(const igraph_t * graph,igraph_vector_int_list_t * separators);
// 
// // the following function fuzzes igraph_minimum_size_separators
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//     // First, we need to check if the size of the input is valid
//     if (Size <= 1) {      // Changed to 1 because Data[0] is accessed
//         return 0;
//     }
// 
//     // Next, we need to initialize a graph object
//     igraph_t graph;
//     igraph_empty(&graph, 0, IGRAPH_UNDIRECTED);
// 
//     // Then, we need to populate the graph object with edges and vertices
//     int num_vertices = (int) Data[0];
//     for (int i = 1; i < Size - 1; i += 2) {      // Changed termination condition to avoid buffer overflow
//         if (i + 1 >= Size) {     // Check if i+1 exceeds the array bounds
//             break;
//         }
//         int source = (int) Data[i];
//         int target = (int) Data[i + 1];
//         igraph_add_edge(&graph, source, target);
//     }
// 
//     // Finally, we can call the target function with our graph object
//     igraph_vector_int_list_t separators;
//     igraph_vector_int_list_init(&separators, 0);
//     igraph_minimum_size_separators(&graph, &separators);
// 
//     // Clean up the graph and vector of separators
//     igraph_destroy(&graph);
//     igraph_vector_int_list_destroy(&separators);
// 
//     return 0;
// }
// ```
// 
// The above C code can be built successfully but will crash (libFuzzer-deadly signal).
// The crash line is:
// igraph_add_edge(&graph, source, target);
// 
// The frames of the stack are:
// #0 0x5391c1 in __sanitizer_print_stack_trace /src/llvm-project/compiler-rt/lib/asan/asan_stack.cpp:87:3
// #1 0x5b9ba5 in igraph_abort /src/igraph/src/core/error.c:69:5
// #2 0x5b9d68 in igraph_error_handler_abort /src/igraph/src/core/error.c:202:5
// #3 0x5b9d68 in igraph_error /src/igraph/src/core/error.c:174:9
// #4 0x572f53 in igraph_add_edges /src/igraph/src/graph/type_indexededgelist.c:261:9
// #5 0x59d2ff in igraph_add_edge /src/igraph/src/operators/add_edge.c:58:5
// #6 0x56a085 in LLVMFuzzerTestOneInput /root/workspace/jarvis/targets/igraph/c/para-iter-account-8-0/dummyfuzzer.c:81:9
// 
// 
// 
// Based on the above information, fix the code.
#include "igraph/igraph_separators.h"

//extern igraph_error_t igraph_minimum_size_separators(const igraph_t * graph,igraph_vector_int_list_t * separators);

// the following function fuzzes igraph_minimum_size_separators
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    // First, we need to check if the size of the input is valid
    if (Size <= 1) {      // Changed to 1 because Data[0] is accessed
        return 0;
    }

    // Next, we need to initialize a graph object
    igraph_t graph;
    igraph_empty(&graph, (int)Data[0], IGRAPH_UNDIRECTED);

    int num_vertices = igraph_vcount(&graph);

    // Then, we need to populate the graph object with edges and vertices
    for (int i = 1; i < Size - 1; i += 2) {      // Changed termination condition to avoid buffer overflow
        if (i + 1 >= Size) {     // Check if i+1 exceeds the array bounds
            break;
        }
        int source = (int) Data[i];
        int target = (int) Data[i + 1];
        if (source >= 0 && source < num_vertices && target >= 0 && target < num_vertices) {
            igraph_add_edge(&graph, source, target);
        }
        // ignore source/target values outside the valid range of [0, num_vertices-1]
    }

    // Finally, we can call the target function with our graph object
    igraph_vector_int_list_t separators;
    igraph_vector_int_list_init(&separators, 0);
    igraph_minimum_size_separators(&graph, &separators);

    // Clean up the graph and vector of separators
    igraph_destroy(&graph);
    igraph_vector_int_list_destroy(&separators);

    return 0;
}