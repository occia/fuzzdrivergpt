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

// The following is a fuzz driver written in C language, complete the implementation. Output the continued code in reply only.

#include "inchi_api.h"

// @ examples of API usage from INCHI_API/libinchi/src/ixa/ixa_inchikey_builder.c-IXA_INCHIKEYBUILDER_GetInChIKey
// const char* INCHI_DECL IXA_INCHIKEYBUILDER_GetInChIKey( IXA_STATUS_HANDLE hStatus,
//                                                         IXA_INCHIKEYBUILDER_HANDLE hKeyBuilder )
// {
//     INCHIKEYBUILDER* key_builder = KEYBUILDER_Unpack( hStatus, hKeyBuilder );
//     if (!key_builder) return NULL;
// 
//     if (key_builder->dirty)
//     {
//         char extra1[256];
//         char extra2[256];
//         if (GetINCHIKeyFromINCHI( key_builder->inchi, 0, 0, key_builder->inchi_key, extra1, extra2 ) != INCHIKEY_OK)
//         {
//             printf( "Failed to create InChIKey\n" );
//             return NULL;
//         }
//         key_builder->dirty = 0;
//     }
// 
//     return key_builder->inchi_key;
// }

//extern int GetINCHIKeyFromINCHI(const char * szINCHISource,const int xtra1,const int xtra2,char * szINCHIKey,char * szXtra1,char * szXtra2);

// the following function fuzzes GetINCHIKeyFromINCHI based on the above API usages
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
const int max_szInchiSize = 1024;
    const int max_szXtraSize = 256;

    char szINCHISource[max_szInchiSize + 1];
    char szINCHIKey[28]; // defined by the inchi key format
    char szXtra1[max_szXtraSize + 1];
    char szXtra2[max_szXtraSize + 1];

    if (Size < 1)
        return 0;

    size_t szInchiSize = Size > max_szInchiSize ? max_szInchiSize : Size;
    memcpy(szINCHISource, Data, szInchiSize);
    szINCHISource[szInchiSize] = '\0';

    GetINCHIKeyFromINCHI(szINCHISource, 0, 0, szINCHIKey, szXtra1, szXtra2);

    return 0;
}