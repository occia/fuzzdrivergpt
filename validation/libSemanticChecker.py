
class BaseChecker:
	ty = 'BASECHECKER'
	category = None

	funcsig = None

	def do_check(self, arg):
		raise Exception('Not implemented')

class FPChecker(BaseChecker):
	ty = 'FPCHECKER'
	category = 'FP'

class SemanticTester(FPChecker):
	ty = 'SEMATESTER'

	funcsig = None
	check_func = None
	check_func_decl = None
	testcases = None
	main_func = '''
static const uint8_t * sema_data = NULL;
static int sema_size = 0;

void load_input_of_sematester(const char * filename) {
	char *source = NULL;
	FILE *fp = fopen(filename, "r");
	if (fp == NULL) {
		printf("Open input %s meets error: errno = %d: %s\\n", filename, errno, strerror(errno));
		return;
	}

	/* Go to the end of the file. */
	if (fseek(fp, 0L, SEEK_END) == 0) {
		/* Get the size of the file. */
		sema_size = ftell(fp);
		if (sema_size == -1) { 
			/* Error */
			printf("sema_size of %s is -1, errno = %d: %s\\n", filename, errno, strerror(errno));
			return;
		}

		/* Allocate our buffer to that size. */
		source = malloc(sizeof(char) * sema_size);

		/* Go back to the start of the file. */
		if (fseek(fp, 0L, SEEK_SET) != 0) {
			/* Error */
			printf("fseek of %s error: errno = %d: %s\\n", filename, errno, strerror(errno));
			return;
		}

		/* Read the entire file into memory. */
		size_t newLen = fread(source, sizeof(char), sema_size, fp);
		if ( ferror( fp ) != 0 ) {
			printf("Error reading file %s\\n", filename);
			return;
		}
	}

	fclose(fp);

	// caller frees the source
	sema_data = (const uint8_t *) source;
}

int main(int argc, char *argv[]) {
	load_input_of_sematester(argv[1]);
	if ( (sema_data == NULL) || (sema_size < 0) )
		exit(1);

	// printf("sema_data: %s\\nsema_size: %d\\n", sema_data, sema_size);
	// printf("sema_size: %d\\n", sema_size);

	LLVMFuzzerTestOneInput(sema_data, sema_size);
	
	return 0;
}
'''

	def hook_api_func(self, code):
		# replace the api func
		return code.replace('%s(' % (self.funcsig), 'check_%s(' % (self.funcsig))

	def add_func_decl(self, code):
		# add the api decl
		return code.replace('extern int LLVMFuzzerTestOneInput', self.check_func_decl + '\nextern int LLVMFuzzerTestOneInput')

	def gen_test_code(self, code):
		test_code = '''
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
''' + code
		test_code = self.hook_api_func(test_code)
		test_code = self.add_func_decl(test_code)

		return '\n'.join([ test_code, self.check_func, self.main_func ])

	def do_check(self, dotestfunc):
		raise Exception('Not implemented')

class igraph_edge_connectivity_Checker(SemanticTester):

	funcsig = 'igraph_edge_connectivity'
	check_func = '''
igraph_error_t check_igraph_edge_connectivity(const igraph_t * arg1,igraph_integer_t * arg2,igraph_bool_t arg3) {
	igraph_vector_int_t edges;
	long int no_of_edges = igraph_ecount(arg1);

	IGRAPH_VECTOR_INT_INIT_FINALLY(&edges, 0);
	igraph_get_edgelist(arg1, &edges, 0);

	printf("SEMA-CHECK-CONTENT:");
	for (size_t i = 0; i < no_of_edges; ++i) {
		printf("%c", (int) VECTOR(edges)[i]);
	}
	printf("\\n");

	exit(0);

	return 0;
}
'''
	check_func_decl = 'extern igraph_error_t check_igraph_edge_connectivity(const igraph_t * arg1,igraph_integer_t * arg2,igraph_bool_t arg3);'
	testcases = [ 'A' * 8, 'A' * 8 + '\0', 'A' * 16, 'A' * 16 + '\0', 'A' * 64, 'A' * 64 + '\0' ]
	main_func = SemanticTester.main_func

	def do_check(self, dotestfunc):
		results = {}
		for testcase in self.testcases:
			result = dotestfunc(testcase)
			results[testcase] = result
			if 'SEMA-CHECK-CONTENT:A' in result:
				# any one case works is ok
				return True, result
		
		return False, '\n'.join([ 'Log of case %s:\n%s\n' % (case, log) for case, log in results.items() ])

class stun_is_response_Checker(SemanticTester):
	funcsig = 'stun_is_response'
	check_func = '''
int check_stun_is_response(const stun_buffer * arg1) {
	printf("SEMA-CHECK-CONTENT:");
	for (size_t i = 0; i < arg1->len; ++i) {
		printf("%c", (uint8_t)arg1->buf[i]);
	}
	printf("\\n");

	exit(0);

	return 0;
}
'''
	check_func_decl = 'extern int check_stun_is_response(const stun_buffer * arg1);'
	testcases = [ 'A' * 8, 'A' * 8 + '\0', 'A' * 16, 'A' * 16 + '\0', 'A' * 64, 'A' * 64 + '\0' ]
	main_func = SemanticTester.main_func

	def do_check(self, dotestfunc):
		results = {}
		for testcase in self.testcases:
			result = dotestfunc(testcase)
			results[testcase] = result
			if 'SEMA-CHECK-CONTENT:AAAA' in result:
				# any one case works is ok
				return True, result

		return False, '\n'.join([ 'Log of case %s:\n%s\n' % (case, log) for case, log in results.items() ])

class gdk_pixbuf_animation_new_from_file_Checker(SemanticTester):
	funcsig = 'gdk_pixbuf_animation_new_from_file'
	check_func = '''
GdkPixbufAnimation * check_gdk_pixbuf_animation_new_from_file(const char * arg1,GError ** arg2) {
	// 1. file need exist
	// 2. file content not match

	FILE * fPtr = NULL;
	char ch = 0;
	fPtr = fopen(arg1, "r");
	if (fPtr == NULL) {
		// not exist
		printf("Open %s meets error: errno = %d: %s\\n", arg1, errno, strerror(errno));
		exit(0);
	}

	printf("SEMA-CHECK-CONTENT:");
	do {
		ch = fgetc(fPtr);
		printf("%c", ch);
	} while (ch != EOF);
	printf("\\n");

	fclose(fPtr);
	exit(0);

	return 0;
}
'''
	check_func_decl = "extern GdkPixbufAnimation * check_gdk_pixbuf_animation_new_from_file(const char * arg1,GError ** arg2);"
	testcases = [ 'A' * 8, 'A' * 8 + '\0', 'A' * 16, 'A' * 16 + '\0', 'A' * 64, 'A' * 64 + '\0' ]
	main_func = SemanticTester.main_func

	def do_check(self, dotestfunc):
		results = {}
		for testcase in self.testcases:
			result = dotestfunc(testcase)
			results[testcase] = result
			if 'SEMA-CHECK-CONTENT:AAAA' in result:
				# any one case works is ok
				return True, result
			
		return False, '\n'.join([ 'Log of case %s:\n%s\n' % (case, log) for case, log in results.items() ])

class gdk_pixbuf_new_from_file_Checker(SemanticTester):
	funcsig = 'gdk_pixbuf_new_from_file'
	check_func = '''
GdkPixbuf * check_gdk_pixbuf_new_from_file(const char * arg1,GError ** arg2) {
	// 1. file need exist
	// 2. file content not match

	FILE * fPtr = NULL;
	char ch = 0;
	fPtr = fopen(arg1, "r");
	if (fPtr == NULL) {
		// not exist
		printf("Open %s meets error: errno = %d: %s\\n", arg1, errno, strerror(errno));
		exit(0);
	}

	printf("SEMA-CHECK-CONTENT:");
	do {
		ch = fgetc(fPtr);
		printf("%c", ch);
	} while (ch != EOF);
	printf("\\n");

	fclose(fPtr);
	exit(0);

	return 0;
}
'''
	check_func_decl = "extern GdkPixbuf * check_gdk_pixbuf_new_from_file(const char * arg1,GError ** arg2);"
	testcases = [ 'A' * 8, 'A' * 8 + '\0', 'A' * 16, 'A' * 16 + '\0', 'A' * 64, 'A' * 64 + '\0' ]
	main_func = SemanticTester.main_func

	def do_check(self, dotestfunc):
		results = {}
		for testcase in self.testcases:
			result = dotestfunc(testcase)
			results[testcase] = result
			if 'SEMA-CHECK-CONTENT:AAAA' in result:
				# any one case works is ok
				return True, result

		return False, '\n'.join([ 'Log of case %s:\n%s\n' % (case, log) for case, log in results.items() ])

class gdk_pixbuf_new_from_file_at_scale_Checker(SemanticTester):
	funcsig = 'gdk_pixbuf_new_from_file_at_scale'
	check_func = '''
GdkPixbuf * check_gdk_pixbuf_new_from_file_at_scale(const char * arg1,int arg2,int arg3,gboolean arg4,GError ** arg5) {
	// 1. file need exist
	// 2. file content not match

	FILE * fPtr = NULL;
	char ch = 0;
	fPtr = fopen(arg1, "r");
	if (fPtr == NULL) {
		// not exist
		printf("Open %s meets error: errno = %d: %s\\n", arg1, errno, strerror(errno));
		exit(0);
	}

	printf("SEMA-CHECK-CONTENT:");
	do {
		ch = fgetc(fPtr);
		printf("%c", ch);
	} while (ch != EOF);
	printf("\\n");

	fclose(fPtr);
	exit(0);

	return 0;
}
'''
	check_func_decl = "extern GdkPixbuf * check_gdk_pixbuf_new_from_file_at_scale(const char * arg1,int arg2,int arg3,gboolean arg4,GError ** arg5);"
	testcases = [ 'A' * 8, 'A' * 8 + '\0', 'A' * 16, 'A' * 16 + '\0', 'A' * 64, 'A' * 64 + '\0' ]
	main_func = SemanticTester.main_func

	def do_check(self, dotestfunc):
		results = {}
		for testcase in self.testcases:
			result = dotestfunc(testcase)
			results[testcase] = result
			if 'SEMA-CHECK-CONTENT:AAAA' in result:
				# any one case works is ok
				return True, result

		return False, '\n'.join([ 'Log of case %s:\n%s\n' % (case, log) for case, log in results.items() ])

class gf_isom_open_file_Checker(SemanticTester):
	funcsig = 'gf_isom_open_file'
	check_func = '''
GF_ISOFile * check_gf_isom_open_file(const char * arg1,GF_ISOOpenMode arg2,const char * arg3) {
	// 1. file need exist
	// 2. file content not match

	FILE * fPtr = NULL;
	char ch = 0;
	fPtr = fopen(arg1, "r");
	if (fPtr == NULL) {
		// not exist
		printf("Open %s meets error: errno = %d: %s\\n", arg1, errno, strerror(errno));
		exit(0);
	}

	printf("SEMA-CHECK-CONTENT:");
	do {
		ch = fgetc(fPtr);
		printf("%c", ch);
	} while (ch != EOF);
	printf("\\n");

	fclose(fPtr);
	exit(0);

	return 0;
}
'''
	check_func_decl = "extern GF_ISOFile * check_gf_isom_open_file(const char * arg1,GF_ISOOpenMode arg2,const char * arg3);"
	testcases = [ 'A' * 8, 'A' * 8 + '\0', 'A' * 16, 'A' * 16 + '\0', 'A' * 64, 'A' * 64 + '\0' ]
	main_func = SemanticTester.main_func

	def do_check(self, dotestfunc):
		results = {}
		for testcase in self.testcases:
			result = dotestfunc(testcase)
			results[testcase] = result
			if 'SEMA-CHECK-CONTENT:AAAA' in result:
				# any one case works is ok
				return True, result

		return False, '\n'.join([ 'Log of case %s:\n%s\n' % (case, log) for case, log in results.items() ])

class dwarf_init_path_Checker(SemanticTester):
	funcsig = 'dwarf_init_path'
	check_func = '''
int check_dwarf_init_path(const char * arg1,char * arg2,unsigned int arg3,unsigned int arg4,Dwarf_Handler arg5,Dwarf_Ptr arg6,Dwarf_Debug * arg7,Dwarf_Error * arg8) {
	// 1. file need exist
	// 2. file content not match

	FILE * fPtr = NULL;
	char ch = 0;
	fPtr = fopen(arg1, "r");
	if (fPtr == NULL) {
		// not exist
		printf("Open %s meets error: errno = %d: %s\\n", arg1, errno, strerror(errno));
		exit(0);
	}

	printf("SEMA-CHECK-CONTENT:");
	do {
		ch = fgetc(fPtr);
		printf("%c", ch);
	} while (ch != EOF);
	printf("\\n");

	fclose(fPtr);
	exit(0);

	return 0;
}
'''
	check_func_decl = "extern int check_dwarf_init_path(const char * arg1,char * arg2,unsigned int arg3,unsigned int arg4,Dwarf_Handler arg5,Dwarf_Ptr arg6,Dwarf_Debug * arg7,Dwarf_Error * arg8);"
	testcases = [ 'A' * 8, 'A' * 8 + '\0', 'A' * 16, 'A' * 16 + '\0', 'A' * 64, 'A' * 64 + '\0' ]
	main_func = SemanticTester.main_func

	def do_check(self, dotestfunc):
		results = {}
		for testcase in self.testcases:
			result = dotestfunc(testcase)
			results[testcase] = result
			if 'SEMA-CHECK-CONTENT:AAAA' in result:
				# any one case works is ok
				return True, result

		return False, '\n'.join([ 'Log of case %s:\n%s\n' % (case, log) for case, log in results.items() ])

class ixmlLoadDocumentEx_Checker(SemanticTester):
	funcsig = 'ixmlLoadDocumentEx'
	check_func = '''
int check_ixmlLoadDocumentEx(const char * arg1,IXML_Document ** arg2) {
	// 1. file need exist
	// 2. file content not match

	FILE * fPtr = NULL;
	char ch = 0;
	fPtr = fopen(arg1, "r");
	if (fPtr == NULL) {
		// not exist
		printf("Open %s meets error: errno = %d: %s\\n", arg1, errno, strerror(errno));
		exit(0);
	}

	printf("SEMA-CHECK-CONTENT:");
	do {
		ch = fgetc(fPtr);
		printf("%c", ch);
	} while (ch != EOF);
	printf("\\n");

	fclose(fPtr);
	exit(0);

	return 0;
}
'''
	check_func_decl = "extern int check_ixmlLoadDocumentEx(const char * arg1,IXML_Document ** arg2);"
	testcases = [ 'A' * 8, 'A' * 8 + '\0', 'A' * 16, 'A' * 16 + '\0', 'A' * 64, 'A' * 64 + '\0' ]
	main_func = SemanticTester.main_func

	def do_check(self, dotestfunc):
		results = {}
		for testcase in self.testcases:
			result = dotestfunc(testcase)
			results[testcase] = result
			if 'SEMA-CHECK-CONTENT:AAAA' in result:
				# any one case works is ok
				return True, result

		return False, '\n'.join([ 'Log of case %s:\n%s\n' % (case, log) for case, log in results.items() ])

class CodeChecker(FPChecker):
	ty = 'CODECHECKER'
	funcsig = None

	def do_check(self, code):
		raise Exception('Not implemented')

class get_src_address_socket_Checker(CodeChecker):
	funcsig = 'get_src_address_socket'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class get_src_uri_Checker(CodeChecker):
	funcsig = 'get_src_uri'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_content_disposition_Checker(CodeChecker):
	funcsig = 'parse_content_disposition'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_diversion_header_Checker(CodeChecker):
	funcsig = 'parse_diversion_header'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_from_header_Checker(CodeChecker):
	funcsig = 'parse_from_header'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_from_uri_Checker(CodeChecker):
	funcsig = 'parse_from_uri'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_headers_Checker(CodeChecker):
	funcsig = 'parse_headers'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_identityinfo_header_Checker(CodeChecker):
	funcsig = 'parse_identityinfo_header'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_pai_header_Checker(CodeChecker):
	funcsig = 'parse_pai_header'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_privacy_Checker(CodeChecker):
	funcsig = 'parse_privacy'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_record_route_headers_Checker(CodeChecker):
	funcsig = 'parse_record_route_headers'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_refer_to_header_Checker(CodeChecker):
	funcsig = 'parse_refer_to_header'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_route_headers_Checker(CodeChecker):
	funcsig = 'parse_route_headers'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_to_header_Checker(CodeChecker):
	funcsig = 'parse_to_header'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class parse_to_uri_Checker(CodeChecker):
	funcsig = 'parse_to_uri'

	def do_check(self, code):
		for line in code.split('\n'):
			if not line.strip().startswith('//'):
				if not line.strip().startswith('extern'):
					if 'parse_msg(' in code:
						return True, 'parse_msg function found'
		return False, 'parse_msg function not found'

class AlwaysInvalidChecker(FPChecker):
	ty = 'ALWAYSINVALIDCHECKER'
	funcsig = None

	def do_check(self, code):
		return False, 'Always invalid due to the miss of server'

class civetweb_mg_get_response_Checker(AlwaysInvalidChecker):
	funcsig = 'mg_get_response'

class libmodbus_modbus_read_bits_Checker(AlwaysInvalidChecker):
	funcsig = 'modbus_read_bits'

class libmodbus_modbus_read_registers_Checker(AlwaysInvalidChecker):
	funcsig = 'modbus_read_registers'

class libmodbus_modbus_receive_Checker(AlwaysInvalidChecker):
	funcsig = 'modbus_receive'

class FNChecker(BaseChecker):
	ty = 'FNCHECKER'
	category = 'FN'

checker_list = [
	###
	# FP checkers
	###
	# SemanticTester
	igraph_edge_connectivity_Checker,
	stun_is_response_Checker,
	gdk_pixbuf_animation_new_from_file_Checker,
	gdk_pixbuf_new_from_file_Checker,
	gdk_pixbuf_new_from_file_at_scale_Checker,
	gf_isom_open_file_Checker,
	dwarf_init_path_Checker,
	ixmlLoadDocumentEx_Checker,
	# CodeChecker
	get_src_address_socket_Checker,
	get_src_uri_Checker,
	parse_content_disposition_Checker,
	parse_diversion_header_Checker,
	parse_from_header_Checker,
	parse_from_uri_Checker,
	parse_headers_Checker,
	parse_identityinfo_header_Checker,
	parse_pai_header_Checker,
	parse_privacy_Checker,
	parse_record_route_headers_Checker,
	parse_refer_to_header_Checker,
	parse_route_headers_Checker,
	parse_to_header_Checker,
	parse_to_uri_Checker,
	# AlwaysInvalidChecker
	#civetweb_mg_get_response_Checker,
	#libmodbus_modbus_read_bits_Checker,
	#libmodbus_modbus_read_registers_Checker,
	#libmodbus_modbus_receive_Checker,
	###
	# FN checkers
	###
]

fp_checkers = None
fn_checkers = None

def get_fp_checkers(funcsig):
	global fp_checkers

	if fp_checkers == None:
		fp_checkers = {}
		for checker in checker_list:
			if checker.category == 'FP':
				if checker.funcsig not in fp_checkers:
					fp_checkers[checker.funcsig] = []
				fp_checkers[checker.funcsig].append(checker())

	return fp_checkers.get(funcsig, [])

def get_fn_checkers(funcsig):
	global fn_checkers

	if fn_checkers == None:
		fn_checkers = {}
		for checker in checker_list:
			if checker.category == 'FN':
				if checker.funcsig not in fn_checkers:
					fn_checkers[checker.funcsig] = []
				fn_checkers[checker.funcsig].append(checker())

	return fn_checkers.get(funcsig, [])
