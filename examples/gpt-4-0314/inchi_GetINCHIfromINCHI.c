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
// // Function to validate InChI string according to InChI guidelines
// int isValidInchiString(const char *InChI_str, size_t str_len) {
//     if (str_len < 5 || InChI_str[0] != 'I' || InChI_str[1] != 'n' || InChI_str[2] != 'C' || InChI_str[3] != 'h' || InChI_str[4] != 'I') {
//         return 0;
//     }
//     if (InChI_str[str_len] != '\0') {
//         return 0;
//     }
//     for (size_t i = 0; i < str_len; ++i) {
//         if (InChI_str[i] == '\0') {
//             return 0;
//         }
//     }
//     return 1;
// }
// 
// extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
//     inchi_InputINCHI inpInChI;
//     inchi_Output out;
// 
//     if (Size < 5) {
//         return 0;
//     }
// 
//     // Initialize inchi_InputINCHI structure
//     inpInChI.szInChI = (char*)malloc(Size + 1);
//     if (!inpInChI.szInChI) {
//         return 0;
//     }
// 
//     // Copy input data to inchi_InputINCHI.szInChI
//     memcpy(inpInChI.szInChI, Data, Size);
//     inpInChI.szInChI[Size] = '\0';
// 
//     // Check if the input string is valid InChI
//     if (!isValidInchiString(inpInChI.szInChI, Size)) {
//         free(inpInChI.szInChI);
//         return 0;
//     }
// 
//     // Fuzz GetINCHIfromINCHI
//     int ret = GetINCHIfromINCHI(&inpInChI, &out);
//     if (ret != inchi_Ret_OKAY) {
//         free(inpInChI.szInChI);
//         return 0;
//     }
// 
//     // Free memory and reset output structure
//     free(inpInChI.szInChI);
//     FreeINCHI(&out);
// 
//     return 0;
// }
// ```
// 
// The above C code can be built successfully but will crash (ASAN-SEGV on unknown address 0x000000000003 (pc 0x7effd90266e5 bp 0x7ffc925de490 sp 0x7ffc925ddc48 T0)).
// 
// 
// The frames of the stack are:
// #0 0x7effd90266e5  (/lib/x86_64-linux-gnu/libc.so.6+0x1886e5) (BuildId: 1878e6b475720c7c51969e69ab2d276fae6d1dee)
// #1 0x4c3c48 in __interceptor_strlen /src/llvm-project/compiler-rt/lib/asan/../sanitizer_common/sanitizer_common_interceptors.inc
// #2 0x56e6ec in GetINCHIfromINCHI /src/INCHI-1-SRC/INCHI_API/libinchi/src/inchi_dll.c:2187:55
// #3 0x56a611 in LLVMFuzzerTestOneInput (/root/workspace/jarvis/targets/inchi/c/para-iter-account-10-0/dummyfuzzer+0x56a611)
// 
// 
// 
// Based on the above information, fix the code.
#include "inchi_api.h"

// Function to validate InChI string according to InChI guidelines
int isValidInchiString(const char *InChI_str, size_t str_len) {
    if (str_len < 5 || InChI_str[0] != 'I' || InChI_str[1] != 'n' || InChI_str[2] != 'C' || InChI_str[3] != 'h' || InChI_str[4] != 'I') {
        return 0;
    }
    if (InChI_str[str_len - 1] != '\0') {
        return 0;
    }
    for (size_t i = 0; i < str_len; ++i) {
        if (InChI_str[i] == '\0') {
            return 0;
        }
    }
    return 1;
}

extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    inchi_InputINCHI inpInChI;
    inchi_Output out;

    if (Size < 5) {
        return 0;
    }

    // Initialize inchi_InputINCHI structure
    inpInChI.szInChI = (char*)malloc(Size + 1);
    if (!inpInChI.szInChI) {
        return 0;
    }

    // Copy input data to inchi_InputINCHI.szInChI
    memcpy(inpInChI.szInChI, Data, Size);
    inpInChI.szInChI[Size] = '\0';

    // Check if the input string is valid InChI
    if (!isValidInchiString(inpInChI.szInChI, Size)) {
        free(inpInChI.szInChI);
        return 0;
    }

    // Fuzz GetINCHIfromINCHI
    int ret = GetINCHIfromINCHI(&inpInChI, &out);
    if (ret != inchi_Ret_OKAY) {
        free(inpInChI.szInChI);
        return 0;
    }

    // Free memory and reset output structure
    free(inpInChI.szInChI);
    FreeINCHI(&out);

    return 0;
}