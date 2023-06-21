#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>

#include "igraph/igraph.h"

// ```
// #include "igraph/igraph_topology.h"
// 
// // @ examples of API usage from igraph/igraph/tests/unit/isomorphism_test.c-test_bliss
// // void test_bliss(void) {
// //     igraph_t ring1, ring2, directed_ring;
// //     igraph_vector_int_t perm;
// //     igraph_bool_t iso;
// //     igraph_bliss_info_t info;
// //     igraph_vector_int_t color;
// //     igraph_vector_int_list_t generators;
// // 
// //     igraph_ring(&ring1, 100, /*directed=*/ 0, /*mutual=*/ 0, /*circular=*/1);
// //     igraph_vector_int_init_range(&perm, 0, igraph_vcount(&ring1));
// //     random_permutation(&perm);
// //     igraph_permute_vertices(&ring1, &ring2, &perm);
// // 
// //     igraph_ring(&directed_ring, 100, /* directed= */ 1, /* mutual = */0, /* circular = */1);
// // 
// //     igraph_vector_int_list_init(&generators, 0);
// // 
// //     igraph_isomorphic_bliss(&ring1, &ring2, NULL, NULL, &iso, NULL, NULL, IGRAPH_BLISS_F, NULL, NULL);
// //     if (! iso) {
// //         printf("Bliss failed on ring isomorphism.\n");
// //     }
// // 
// //     igraph_count_automorphisms(&ring1, NULL, IGRAPH_BLISS_F, &info);
// //     if (strcmp(info.group_size, "200") != 0) {
// //         printf("Biss automorphism count failed: ring1.\n");
// //     }
// //     igraph_free(info.group_size);
// // 
// //     igraph_count_automorphisms(&ring2, NULL, IGRAPH_BLISS_F, &info);
// //     if (strcmp(info.group_size, "200") != 0) {
// //         printf("Biss automorphism count failed: ring2.\n");
// //     }
// //     igraph_free(info.group_size);
// // 
// //     igraph_count_automorphisms(&directed_ring, NULL, IGRAPH_BLISS_F, &info);
// //     if (strcmp(info.group_size, "100") != 0) {
// //         printf("Biss automorphism count failed: directed_ring.\n");
// //     }
// //     igraph_free(info.group_size);
// // 
// //     // The follwing test is included so there is at least one call to igraph_automorphism_group
// //     // in the test suite. However, the generator set returned may depend on the splitting
// //     // heursitics as well as on the Bliss version. If the test fails, please verify manually
// //     // that the generating set is valid. For a undirected cycle graph like ring2, there should
// //     // be two generators: a cyclic permutation and a reversal of the vertex order.
// //     igraph_automorphism_group(&ring2, NULL, &generators, IGRAPH_BLISS_F, NULL);
// //     if (igraph_vector_int_list_size(&generators) != 2)
// //         printf("Bliss automorphism generators may have failed with ring2. "
// //                "Please verify the generators manually. "
// //                "Note that the generator set is not guaranteed to be minimal.\n");
// //     igraph_vector_int_list_clear(&generators);
// // 
// //     // For a directed ring, the only generator should be a cyclic permutation.
// //     igraph_automorphism_group(&directed_ring, NULL, &generators, IGRAPH_BLISS_F, NULL);
// //     if (igraph_vector_int_list_size(&generators) != 1)
// //         printf("Bliss automorphism generators may have failed with directed_ring. "
// //                "Please verify the generators manually. "
// //                "Note that the generator set is not guaranteed to be minimal.\n");
// //     igraph_vector_int_list_clear(&generators);
// // 
// //     igraph_vector_int_init_range(&color, 0, igraph_vcount(&ring1));
// // 
// //     igraph_count_automorphisms(&ring1, &color, IGRAPH_BLISS_F, &info);
// //     if (strcmp(info.group_size, "1") != 0) {
// //         printf("Bliss automorphism count with color failed: ring1.\n");
// //     }
// //     igraph_free(info.group_size);
// // 
// //     // There's only one automorphism for this coloured graph, so the generating set is empty.
// //     igraph_automorphism_group(&ring1, &color, &generators, IGRAPH_BLISS_F, NULL);
// //     if (igraph_vector_int_list_size(&generators) != 0) {
// //         printf("Bliss automorphism generators failed with colored graph.\n");
// //     }
// // 
// //     igraph_vector_int_list_destroy(&generators);
// // 
// //     igraph_vector_int_destroy(&color);
// // 
// //     igraph_vector_int_destroy(&perm);
// // 
// //     igraph_destroy(&ring1);
// //     igraph_destroy(&ring2);
// //     igraph_destroy(&directed_ring);
// // }
// 
// //extern igraph_integer_t igraph_vcount(const igraph_t * graph);
// //extern igraph_error_t igraph_ring(igraph_t * graph,igraph_integer_t n,igraph_bool_t directed,igraph_bool_t mutual,igraph_bool_t circular);
// //extern igraph_error_t igraph_permute_vertices(const igraph_t * graph,igraph_t * res,const igraph_vector_int_t * permutation);
// //extern void igraph_free(void * ptr);
// //extern igraph_error_t igraph_automorphism_group(const igraph_t * graph,const igraph_vector_int_t * colors,igraph_vector_int_list_t * generators,igraph_bliss_sh_t sh,igraph_bliss_info_t * info);
// //extern void igraph_destroy(igraph_t * graph);
// //extern igraph_error_t igraph_isomorphic_bliss(const igraph_t * graph1,const igraph_t * graph2,const igraph_vector_int_t * colors1,const igraph_vector_int_t * colors2,igraph_bool_t * iso,igraph_vector_int_t * map12,igraph_vector_int_t * map21,igraph_bliss_sh_t sh,igraph_bliss_info_t * info1,igraph_bliss_info_t * info2);
// 
// // the following function fuzzes igraph_automorphism_group based on the above API usages
// extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
// // First, let's initialize the necessary variables and structures
//     igraph_t graph1, graph2;
//     igraph_vector_int_t perm, color;
//     igraph_vector_int_list_t generators;
//     igraph_bool_t iso;
//     igraph_bliss_info_t info;
// 
//     // Create a ring graph with random number of vertices between 2 and 100
//     igraph_ring(&graph1, rand() % 99 + 2, /*directed=*/ 0, /*mutual=*/ 0, /*circular=*/1);
// 
//     // Permute the vertices randomly
//     igraph_vector_int_init_range(&perm, 0, igraph_vcount(&graph1));
//     random_permutation(&perm);
//     igraph_permute_vertices(&graph1, &graph2, &perm);
// 
//     // Generate the automorphism group using Bliss algorithm
//     igraph_vector_int_list_init(&generators, 0);
//     igraph_automorphism_group(&graph2, NULL, &generators, IGRAPH_BLISS_F, NULL);
// 
//     // Free the memory and destroy the graphs
//     igraph_vector_int_list_destroy(&generators);
//     igraph_vector_int_destroy(&perm);
//     igraph_destroy(&graph1);
//     igraph_destroy(&graph2);
// 
//     return 0;
// }
// ```
// 
// The above C code calls a non-existing API /root/workspace/jarvis/targets/igraph/c/para-iter-account-3-0/dummyfuzzer.c:123:5: error: use of undeclared identifier 'random_permutation'.
// 
// Based on the above information, fix the code.
#include "igraph/igraph_topology.h"
#include <stdlib.h>

void random_permutation(igraph_vector_int_t *perm) {
    igraph_integer_t i, n = igraph_vector_int_size(perm);
    igraph_integer_t tmp;
    for (i = 0; i < n; i++) {
        igraph_integer_t j = i + rand() % (n - i);
        tmp = VECTOR(*perm)[i];
        VECTOR(*perm)[i] = VECTOR(*perm)[j];
        VECTOR(*perm)[j] = tmp;
    }
}

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    igraph_t graph1, graph2;
    igraph_vector_int_t perm, color;
    igraph_vector_int_list_t generators;
    igraph_bool_t iso;
    igraph_bliss_info_t info;

    igraph_ring(&graph1, rand() % 99 + 2, /*directed=*/ 0, /*mutual=*/ 0, /*circular=*/1);

    igraph_vector_int_init_range(&perm, 0, igraph_vcount(&graph1));
    random_permutation(&perm);
    igraph_permute_vertices(&graph1, &graph2, &perm);

    igraph_vector_int_list_init(&generators, 0);
    igraph_automorphism_group(&graph2, NULL, &generators, IGRAPH_BLISS_F, NULL);

    igraph_vector_int_list_destroy(&generators);
    igraph_vector_int_destroy(&perm);
    igraph_destroy(&graph1);
    igraph_destroy(&graph2);

    return 0;
}