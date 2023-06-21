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

// @ examples of API usage from inchi_js_utils.c-getInChIKeyJson
// char* getInChIKeyJson(char* inchiSource, int xtra1, int xtra2)
// {
// 	char* sInChIKey = (char*)malloc(28);
// 	char* sXtra1 = (char*)malloc(65);
// 	char* sXtra2 = (char*)malloc(65);;
// 	
// 	// memset(sInChIKey, 0, sizeof(*sInChIKey));
// 	// memset(sXtra1, 0, sizeof(*sXtra1));
// 	// memset(sXtra2, 0, sizeof(*sXtra1));
// 	
// 	int rawResult = GetINCHIKeyFromINCHI(inchiSource, xtra1, xtra2, sInChIKey, sXtra1, sXtra2);
// 	
// 	/* Turn into JSON */
// 	char* sSuccess;		
// 	if (rawResult == INCHIKEY_OK)
// 	{
// 		sSuccess = "true";		
// 	}
// 	else
// 	{
// 		sSuccess = "false";						
// 	}
// 	int strSize = _safeStrLen(sInChIKey) + _safeStrLen(sXtra1) + _safeStrLen(sXtra2) + _safeStrLen(sSuccess)
// 			+ _safeStrLen("{'inchiKey':'','xtra1':'','xtra2':'','success':'','errorCode':###}") + 1;
// 	    
// 	char* sResult = (char*)malloc(strSize);
// 	
// 	snprintf(sResult, strSize, "{\"inchiKey\":\"%s\",\"xtra1\":\"%s\",\"xtra2\":\"%s\",\"success\":\"%s\",\"errorCode\":%d}",
// 		_concreateStr(sInChIKey), _concreateStr(sXtra1), _concreateStr(sXtra2), sSuccess, rawResult);
// 		
// 	free(sInChIKey);
// 	free(sXtra1);
// 	free(sXtra2);
// 	
// 	return sResult;
// }

//extern int GetINCHIKeyFromINCHI(const char * szINCHISource,const int xtra1,const int xtra2,char * szINCHIKey,char * szXtra1,char * szXtra2);

// the following function fuzzes GetINCHIKeyFromINCHI based on the above API usages
extern int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
char* inchiSource = (char*)malloc(Size+1); // allocate memory for string
// copy data to inchiSource string
memcpy(inchiSource, Data, Size);
inchiSource[Size] = '\0'; // add null character to terminate string

// prepare variables for GetINCHIKeyFromINCHI function
char* sInChIKey = (char*)malloc(28);
char* sXtra1 = (char*)malloc(65);
char* sXtra2 = (char*)malloc(65);

int xtra1 = 0; // set default value for xtra1
int xtra2 = 0; // set default value for xtra2

// call GetINCHIKeyFromINCHI and store return value in rawResult
int rawResult = GetINCHIKeyFromINCHI(inchiSource, xtra1, xtra2, sInChIKey, sXtra1, sXtra2);

// free memory allocated for inchiSource
free(inchiSource);

// free memory allocated for sInChIKey, sXtra1, and sXtra2
free(sInChIKey);
free(sXtra1);
free(sXtra2);

// return 0 to indicate successful run
return 0;
}