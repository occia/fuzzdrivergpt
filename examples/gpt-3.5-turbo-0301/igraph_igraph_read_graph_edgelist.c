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
// // @ examples of API usage from graphobject.c-igraphmodule_Graph_Read_Edgelist
// // PyObject *igraphmodule_Graph_Read_Edgelist(PyTypeObject * type,
// //                                            PyObject * args, PyObject * kwds)
// // {
// //   igraphmodule_GraphObject *self;
// //   PyObject *directed = Py_True, *fname = NULL;
// //   igraphmodule_filehandle_t fobj;
// //   igraph_t g;
// // 
// //   static char *kwlist[] = { "f", "directed", NULL };
// // 
// //   if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O", kwlist,
// //                                    &fname, &directed))
// //     return NULL;
// // 
// //   if (igraphmodule_filehandle_init(&fobj, fname, "r"))
// //     return NULL;
// // 
// //   if (igraph_read_graph_edgelist(&g, igraphmodule_filehandle_get(&fobj),
// //         0, PyObject_IsTrue(directed))) {
// //     igraphmodule_handle_igraph_error();
// //     igraphmodule_filehandle_destroy(&fobj);
// //     return NULL;
// //   }
// // 
// //   igraphmodule_filehandle_destroy(&fobj);
// //   CREATE_GRAPH_FROM_TYPE(self, g, type);
// // 
// //   return (PyObject *) self;
// // }
// 
// //extern igraph_error_t igraph_read_graph_edgelist(igraph_t * graph,FILE * instream,igraph_integer_t n,igraph_bool_t directed);
// 
// // the following function fuzzes igraph_read_graph_edgelist based on the above API usages
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
// // First, we need to initialize a file handle to read from. We can use a temporary file for this.
//   char* prefix = "fuzz";
//   char* suffix = ".txt";
//   FILE* temp = NULL;
// 
//   if ((temp = tmpfile()) == NULL) {
//     return 0;
//   }
// 
//   // generate an edgelist of random size between 1 and 50 nodes
//   int n = (rand() % 50) + 1;
//   for (int i = 0; i < n; i++) {
//       int num_edges = rand() % n;
//       for (int j = 0; j < num_edges; j++) {
//           int dest_node = rand() % n;
//           // write edge to file, node index starts from 1
//           fprintf(temp, "%d %d\n", i + 1, dest_node + 1);
//       }
//   }
// 
// // Set the file pointer to the beginning of the file
//   if (fseek(temp, 0L, SEEK_SET) != 0) {
//     fclose(temp);
//     return 0;
//   }
// 
// // Initialize igraph
//   igraph_t g;
//   igraph_empty(&g, 0, IGRAPH_UNDIRECTED);
// 
// // Call igraph_read_graph_edgelist with the temporary file handle and a randomly generated value of directed
//   igraph_bool_t directed = rand() % 2;
//   if (igraph_read_graph_edgelist(&g, temp, 0, directed)) {
//     fclose(temp);
//     igraph_destroy(&g);
//     return 0;
//   }
// 
// // Destroy temporary file, igraph and return
//   fclose(temp);
//   igraph_destroy(&g);
//   return 0;
// }
// ```
// 
// The above C code can be built successfully but has runtime memory leak.
// The leak related lines of code are:
//   igraph_empty(&g, 0, IGRAPH_UNDIRECTED);
//   igraph_empty(&g, 0, IGRAPH_UNDIRECTED);
// 
// Based on the above information, fix the code.
#include "igraph/igraph_foreign.h"

// @ examples of API usage from graphobject.c-igraphmodule_Graph_Read_Edgelist
// PyObject *igraphmodule_Graph_Read_Edgelist(PyTypeObject * type,
//                                            PyObject * args, PyObject * kwds)
// {
//   igraphmodule_GraphObject *self;
//   PyObject *directed = Py_True, *fname = NULL;
//   igraphmodule_filehandle_t fobj;
//   igraph_t g;
// 
//   static char *kwlist[] = { "f", "directed", NULL };
// 
//   if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|O", kwlist,
//                                    &fname, &directed))
//     return NULL;
// 
//   if (igraphmodule_filehandle_init(&fobj, fname, "r"))
//     return NULL;
// 
//   if (igraph_read_graph_edgelist(&g, igraphmodule_filehandle_get(&fobj),
//         0, PyObject_IsTrue(directed))) {
//     igraphmodule_handle_igraph_error();
//     igraphmodule_filehandle_destroy(&fobj);
//     return NULL;
//   }
// 
//   igraphmodule_filehandle_destroy(&fobj);
//   CREATE_GRAPH_FROM_TYPE(self, g, type);
// 
//   return (PyObject *) self;
// }

//extern igraph_error_t igraph_read_graph_edgelist(igraph_t * graph,FILE * instream,igraph_integer_t n,igraph_bool_t directed);

// the following function fuzzes igraph_read_graph_edgelist based on the above API usages
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
// First, we need to initialize a file handle to read from. We can use a temporary file for this.
  char* prefix = "fuzz";
  char* suffix = ".txt";
  FILE* temp = NULL;

  if ((temp = tmpfile()) == NULL) {
    return 0;
  }

  // generate an edgelist of random size between 1 and 50 nodes
  int n = (rand() % 50) + 1;
  for (int i = 0; i < n; i++) {
      int num_edges = rand() % n;
      for (int j = 0; j < num_edges; j++) {
          int dest_node = rand() % n;
          // write edge to file, node index starts from 1
          fprintf(temp, "%d %d\n", i + 1, dest_node + 1);
      }
  }

// Set the file pointer to the beginning of the file
  if (fseek(temp, 0L, SEEK_SET) != 0) {
    fclose(temp);
    return 0;
  }

// Initialize igraph
  igraph_t g;
  igraph_bool_t directed = rand() % 2;

// Call igraph_read_graph_edgelist with the temporary file handle and a randomly generated value of directed
  if (igraph_read_graph_edgelist(&g, temp, 0, directed)) {
    fclose(temp);
    return 0;
  }

// Destroy temporary file and igraph before returning
  igraph_destroy(&g);
  fclose(temp);

  return 0;
}