#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include "igraph/igraph.h"

// ```
// #include "igraph/igraph_foreign.h"
// #include <stdio.h>
// #include <stdlib.h>
// #include <string.h>
// #include <unistd.h>
// 
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//     // Check input data
//     if (Data == NULL || Size == 0) {
//         return 0;
//     }
// 
//     // First, we need to create a graph object to pass to igraph_read_graph_gml
//     igraph_t graph;
//     igraph_empty(&graph, 0, false);
//     igraph_error_t error;
// 
//     // Next, we need to create a temporary file to pass to igraph_read_graph_gml
//     char filename[] = "/tmp/fuzzXXXXXX";
//     int fd = mkstemp(filename);
//     if (fd == -1) {
//         igraph_destroy(&graph);
//         return 0;
//     }
//     FILE *file = fdopen(fd, "w");
//     if (file == NULL) {
//         close(fd);
//         igraph_destroy(&graph);
//         return 0;
//     }
//     int ret = fwrite(Data, 1, Size, file);
//     if (ret != Size) {
//         fclose(file);
//         remove(filename);
//         igraph_destroy(&graph);
//         return 0;
//     }
//     fseek(file, 0, SEEK_SET);
// 
//     // Now, we can call igraph_read_graph_gml with the temporary file
//     error = igraph_read_graph_gml(&graph, file);
//     if (error != IGRAPH_SUCCESS) {
//         igraph_destroy(&graph);
//         fclose(file);
//         remove(filename);
//         return 0;
//     }
// 
//     // Finally, we need to free the graph object and delete the temporary file
//     igraph_destroy(&graph);
//     fclose(file);
//     if (remove(filename) != 0) {
//         return 0;
//     }
// 
//     return 0;
// }
// ```
// 
// The above C code can be built successfully but will crash (libFuzzer-deadly signal).
// The crash line is:
// error = igraph_read_graph_gml(&graph, file);
// 
// The frames of the stack are:
// #0 0x5391c1 in __sanitizer_print_stack_trace /src/llvm-project/compiler-rt/lib/asan/asan_stack.cpp:87:3
// #1 0x58e7a5 in igraph_abort /src/igraph/src/core/error.c:69:5
// #2 0x58e968 in igraph_error_handler_abort /src/igraph/src/core/error.c:202:5
// #3 0x58e968 in igraph_error /src/igraph/src/core/error.c:174:9
// #4 0x578ffd in igraph_read_graph_gml /src/igraph/src/io/gml.c:493:9
// #5 0x56a088 in LLVMFuzzerTestOneInput /root/workspace/jarvis/targets/igraph/c/para-iter-account-1-0/dummyfuzzer.c:120:13
// 
// 
// 
// Based on the above information, fix the code.
#include "igraph/igraph_foreign.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    // Check input data
    if (Data == NULL || Size == 0) {
        return 0;
    }

    // First, we need to create a graph object to pass to igraph_read_graph_gml
    igraph_t graph;
    igraph_empty(&graph, 0, false);
    igraph_error_handler_t* old_handler = igraph_set_error_handler(igraph_error_handler_ignore);

    // Next, we need to create a temporary file to pass to igraph_read_graph_gml
    char filename[] = "/tmp/fuzzXXXXXX";
    int fd = mkstemp(filename);
    if (fd == -1) {
        igraph_destroy(&graph);
        igraph_set_error_handler(old_handler);
        return 0;
    }
    FILE *file = fdopen(fd, "w");
    if (file == NULL) {
        close(fd);
        igraph_destroy(&graph);
        igraph_set_error_handler(old_handler);
        return 0;
    }
    int ret = fwrite(Data, 1, Size, file);
    if (ret != Size) {
        fclose(file);
        remove(filename);
        igraph_destroy(&graph);
        igraph_set_error_handler(old_handler);
        return 0;
    }
    fseek(file, 0, SEEK_SET);

    // Now, we can call igraph_read_graph_gml with the temporary file
    igraph_error_t error = igraph_read_graph_gml(&graph, file);
    fclose(file);
    remove(filename);
    igraph_set_error_handler(old_handler);
    if (error != IGRAPH_SUCCESS) {
        igraph_destroy(&graph);
        return 0;
    }

    // Finally, we need to free the graph object
    igraph_destroy(&graph);

    return 0;
}