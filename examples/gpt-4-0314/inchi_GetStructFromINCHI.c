#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <errno.h>

#include "ichi.h"
#include "inchi_api.h"
#include "inchi_gui.h"
#include "inchicmp.h"
#include "ichi_bns.h"
#include "ichi_io.h"
#include "ichicano.h"
#include "ichicant.h"
#include "ichicomn.h"
#include "ichicomp.h"
#include "ichidrp.h"
#include "ichierr.h"
#include "ichimain.h"
#include "ichimake.h"
#include "ichinorm.h"
#include "ichiring.h"
#include "ichirvrs.h"
#include "ichisize.h"
#include "ichister.h"
#include "ichitaut.h"
#include "ichitime.h"
#include "ikey_base26.h"
#include "extr_ct.h"
#include "incomdef.h"
#include "inpdef.h"
#include "ixa.h"
#include "mode.h"
#include "mol_fmt.h"
#include "readinch.h"
#include "sha2.h"
#include "strutil.h"
#include "util.h"
#include "ixa_mol.h"
#include "ixa_status.h"
#include "inchi_dll.h"
#include "inchi_dll_a.h"
#include "inchi_dll_b.h"
#include "inchi_dll_main.h"

// ```
// #include "inchi_api.h"
// 
// // Maximum input size (in bytes) allowed.
// #define MAX_INPUT_SIZE 1024 * 1024
// // Maximum number of components allowed to prevent integer overflow.
// #define MAX_NUM_COMPONENTS (SIZE_MAX / sizeof(INChI))
// 
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//   // Limit the input size to prevent overflow.
//   if (Size > MAX_INPUT_SIZE) {
//     return 0;
//   }
// 
//   inchi_InputINCHI inpInChI;
//   inchi_OutputStruct outStruct;
//   char *input_data = (char *)malloc(Size + 1);
// 
//   if (input_data == NULL) {
//     return 0;
//   }
// 
//   memcpy(input_data, Data, Size);
//   input_data[Size] = '\0';
// 
//   // Initialize the InChI input structure.
//   inpInChI.szInChI = input_data;
//   inpInChI.szOptions = NULL;
// 
//   // Call the fuzzed function.
//   GetStructFromINCHI(&inpInChI, &outStruct);
// 
//   // Free allocated resources.
//   FreeStructFromINCHI(&outStruct);
//   free(input_data);
// 
//   return 0;
// }
// ```
// 
// The above C code can be built successfully but will crash (ASAN-calloc parameters overflow: count * size (-1 * 160) cannot be represented in type size_t (thread T0)).
// 
// 
// The frames of the stack are:
// #0 0x52f1ee in __interceptor_calloc /src/llvm-project/compiler-rt/lib/asan/asan_malloc_linux.cpp:77:3
// #1 0x76d615 in ParseSegmentFormula /src/INCHI-1-SRC/INCHI_BASE/src/ichiread.c:9694:44
// #2 0x746f05 in ReadInChILine /src/INCHI-1-SRC/INCHI_BASE/src/ichiread.c:5111:23
// #3 0x746f05 in InChILine2Data /src/INCHI-1-SRC/INCHI_BASE/src/ichiread.c:2289:11
// #4 0x741aab in ReadWriteInChI /src/INCHI-1-SRC/INCHI_BASE/src/ichiread.c:773:23
// #5 0x578b37 in GetStructFromINCHIEx /src/INCHI-1-SRC/INCHI_API/libinchi/src/inchi_dll.c:2683:16
// #6 0x577708 in GetStructFromINCHI /src/INCHI-1-SRC/INCHI_API/libinchi/src/inchi_dll.c:2835:11
// #7 0x56a0c6 in LLVMFuzzerTestOneInput (/root/workspace/jarvis/targets/inchi/c/para-iter-account-10-0/dummyfuzzer+0x56a0c6)
// 
// The frame `ParseSegmentFormula` related code:
// 9693	/* allocate InChI */
// 9694	if (!( pInpInChI[bMobileH] = (INChI *) inchi_calloc( nNumComponents, sizeof( INChI ) ) ))
// 9695	{
// 
// The frame `ReadInChILine` related code:
// 5110	#endif
// 5111	ret = ParseSegmentFormula( pLine->str, bMobileH, pInpInChI[bReconn],
// 5112	nNumComponents[bReconn], &na_total );
// 
// The frame `InChILine2Data` related code:
// 2288	
// 2289	ret = ReadInChILine( pInp, pLine, pStr, pState, pInpInChI,
// 2290	nNumComponents, nNumProtons, s, bStdFormat,
// 
// The frame `ReadWriteInChI` related code:
// 772	/* Read InChI string */
// 773	nReadStatus = InChILine2Data( pInp, pLine, &strHdr, &pState, &nErr,
// 774	OneInput.pInpInChI, OneInput.nNumComponents,
// 
// The frame `GetStructFromINCHIEx` related code:
// 2682	int num_bonds;
// 2683	nRet = ReadWriteInChI( &ic, &CG , input_file, out_file, log_file,
// 2684	ip, sd, &at, &num_at, &num_bonds,
// 
// The frame `GetStructFromINCHI` related code:
// 2834	
// 2835	ret = GetStructFromINCHIEx( inpInChI, &outex );
// 2836	
// 
// Based on the above information, fix the code.
#include "inchi_api.h"

#define MAX_INPUT_SIZE 1024 * 1024
#define MAX_NUM_COMPONENTS (SIZE_MAX / sizeof(INChI))

extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
  if (Size > MAX_INPUT_SIZE) {
    return 0;
  }

  inchi_InputINCHI inpInChI;
  inchi_OutputStruct outStruct;
  char *input_data = (char *)malloc(Size + 1);

  if (input_data == NULL) {
    return 0;
  }

  memcpy(input_data, Data, Size);
  input_data[Size] = '\0';

  inpInChI.szInChI = input_data;
  inpInChI.szOptions = NULL;

  GetStructFromINCHI(&inpInChI, &outStruct);

  FreeStructFromINCHI(&outStruct);
  free(input_data);

  return 0;
}