# -*- coding: utf-8 -*-
import re

# VR stands for Validated Result
# Corr stands for corrupted
class BasicVR(object):
	ty = None

	def __init__(self):
		pass

	@property
	def detail(self):
		raise Exception('unimplemented')

	@property
	def valid(self):
		raise Exception('unimplemented')

	@property
	def taxon(self):
		raise Exception('unimplemented')

	def toJSON(self):
		raise Exception('unimplemented')
	
	@classmethod
	def load(cls, jsonobj):
		ty = jsonobj['ty']
		if ty == UncheckedVR.ty:
			return UncheckedVR.load(jsonobj)
		elif ty == PartlyCheckedVR.ty:
			return PartlyCheckedVR.load(jsonobj)
		elif ty == ValidVR.ty:
			return ValidVR.load(jsonobj)
		elif ty == UnknownErrVR.ty:
			return UnknownErrVR.load(jsonobj)
		elif ty == CorrErrVR.ty:
			return CorrErrVR.load(jsonobj)
		elif ty == ParseErrVR.ty:
			return ParseErrVR.load(jsonobj)
		elif ty == LinkErrVR.ty:
			return LinkErrVR.load(jsonobj)
		elif ty == FuzzErrVR.ty:
			return FuzzErrVR.load(jsonobj)
		elif ty == SemaErrVR.ty:
			return SemaErrVR.load(jsonobj)
		else:
			raise Exception('Unknown json ty key %s' % (ty))

	@classmethod
	def build(cls):
		raise Exception('unimplemented')

class UncheckedVR(BasicVR):
	ty = 'UNCK'

	def __init__(self):
		super().__init__()

	@property
	def detail(self):
		return "The check has not been started"

	@property
	def valid(self):
		return False

	@property
	def taxon(self):
		return self.ty

	def toJSON(self):
		return {'ty': self.ty}
	
	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty:
			return cls()
		else:
			raise Exception('wrong ty %s' % (jsonobj['ty']))

	@classmethod
	def build(cls):
		r = cls()
		return r.toJSON(), r.detail

class PartlyCheckedVR(BasicVR):
	ty = 'PTCK'

	def __init__(self, detail):
		super().__init__()
		self._detail = detail

	@property
	def detail(self):
		return self._detail

	@property
	def valid(self):
		return False

	@property
	def taxon(self):
		return self.ty

	def toJSON(self):
		return {'ty': self.ty, '_detail': self._detail}
	
	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty:
			return cls(jsonobj['_detail'])
		else:
			raise Exception('wrong ty %s' % (jsonobj['ty']))

	@classmethod
	def build(cls, progress):
		r = cls(progress)
		return r.toJSON(), r.detail

class ValidVR(BasicVR):
	ty = 'VAL'

	def __init__(self, desc):
		super().__init__()
		self._desc = desc

	@property
	def detail(self):
		return "Passed validation\n%s" % (self._desc)

	@property
	def desc(self):
		return self._desc

	@property
	def valid(self):
		return True

	@property
	def taxon(self):
		return self.ty

	def toJSON(self):
		return {'ty': self.ty, '_desc': self._desc}
	
	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty:
			return cls(jsonobj['_desc'])
		else:
			raise Exception('wrong ty %s' % (jsonobj['ty']))

	@classmethod
	def build(cls, log):
		r = cls(log)
		return r.toJSON(), r.detail

	@staticmethod
	def get_cov_info(desc, onlyInitCov=False, onlyDoneCov=False):
		# assume it is a valid desc (init & done cov can be recognized)
		lines = desc.split('\n')
		initline, doneline = None, None
		for line in lines:
			if line.startswith('#'):
				if 'INITED' in line:
					initline = line
				elif 'DONE' in line:
					doneline = line

		initcov = int(initline.split('cov: ')[1].split(' ft:')[0])
		donecov = int(doneline.split('cov: ')[1].split(' ft:')[0])

		if onlyInitCov:
			return initcov

		if onlyDoneCov:
			return donecov

		return initcov, donecov

class InvalidVR(BasicVR):
	def __init__(self, subTy, isDriverErr, desc):
		super().__init__()
		self._subTy = subTy
		self._isDriverErr = isDriverErr
		self._desc = desc

	@property
	def subTy(self):
		return self._subTy

	@property
	def isDriverErr(self):
		return self._isDriverErr

	@property
	def desc(self):
		return self._desc

	@property
	def valid(self):
		return False

	@classmethod
	def load(cls):
		raise Exception('unimplemented')

	@classmethod
	def build(cls):
		raise Exception('unimplemented')

class UnknownErrVR(InvalidVR):
	ty = 'ERR-UNK'

	def __init__(self):
		super().__init__(None, None, None)

	@property
	def taxon(self):
		return self.ty

	def toJSON(self):
		return {'ty': self.ty}

	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty:
			return cls()
		else:
			raise Exception('wrong ty %s' % (jsonobj['ty']))

	@classmethod
	def build(cls):
		r = cls()
		return r.toJSON(), r.detail

class CorrErrVR(InvalidVR):
	ty = 'ERR-CORR'

	def __init__(self, subTy, desc):
		super().__init__(subTy, None, desc)

	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty:
			if jsonobj['_subTy'] == 'NOFN':
				return NoFuncCorrErrVR.load(jsonobj)
			elif jsonobj['_subTy'] == 'INCFN':
				return IncompleteFuncCorrErrVR.load(jsonobj)
			elif jsonobj['_subTy'] == 'NOAPI':
				return NOAPICorrErrVR.load(jsonobj)
			else:
				return ExpCorrErrVR.load(jsonobj)
		else:
			raise Exception('wrong ty %s' % (jsonobj['ty']))

	@classmethod
	def build(cls):
		raise Exception('unimplemented')

class NoFuncCorrErrVR(CorrErrVR):
	def __init__(self):
		super().__init__('NOFN', None)

	@property
	def detail(self):
		return 'Corrupted libclang analysis: No function detected'

	@property
	def taxon(self):
		return self.ty + '-' + self._subTy

	def toJSON(self):
		return {'ty': self.ty, '_subTy': self._subTy}

	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty and jsonobj['_subTy'] == 'NOFN':
			return cls()
		else:
			raise Exception('wrong ty %s or _subTy %s' % (jsonobj['ty'], jsonobj['_subTy']))

	@classmethod
	def build(cls):
		r = cls()
		return r.toJSON(), r.detail

class NOAPICorrErrVR(CorrErrVR):
	def __init__(self):
		super().__init__('NOAPI', None)

	@property
	def detail(self):
		return 'Corrupted libclang analysis: no target API functions are used in fuzz driver'

	@property
	def taxon(self):
		return self.ty + '-' + self._subTy

	def toJSON(self):
		return {'ty': self.ty, '_subTy': self._subTy}

	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty and jsonobj['_subTy'] == 'NOAPI':
			return cls()
		else:
			raise Exception('wrong ty %s or _subTy %s' % (jsonobj['ty'], jsonobj['_subTy']))

	@classmethod
	def build(cls):
		r = cls()
		return r.toJSON(), r.detail

class IncompleteFuncCorrErrVR(CorrErrVR):
	def __init__(self):
		super().__init__('INCFN', None)

	@property
	def detail(self):
		return 'Corrupted libclang analysis: Incomplete function definition for LLVMFuzzerTestOneInput'

	@property
	def taxon(self):
		return self.ty + '-' + self._subTy

	def toJSON(self):
		return {'ty': self.ty, '_subTy': self._subTy}

	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty and jsonobj['_subTy'] == 'INCFN':
			return cls()
		else:
			raise Exception('wrong ty %s or _subTy %s' % (jsonobj['ty'], jsonobj['_subTy']))

	@classmethod
	def build(cls):
		r = cls()
		return r.toJSON(), r.detail

class ExpCorrErrVR(CorrErrVR):
	def __init__(self, subTy, desc):
		super().__init__(subTy, desc)

	@property
	def detail(self):
		return 'Corrupted libclang analysis: %s %s' % (self._subTy, self._desc)

	@property
	def taxon(self):
		return self.ty + '-' + self._subTy

	def toJSON(self):
		return {'ty': self.ty, '_subTy': self._subTy, '_desc': self._desc}

	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty:
			return ExpCorrErrVR(jsonobj['_subTy'], jsonobj['_desc'])
		else:
			raise Exception('wrong ty %s' % (jsonobj['ty']))

	@classmethod
	def build(cls, ex):
		subTy = 'EXP-%s' % (type(ex).__name__)
		desc = str(ex)
		r = ExpCorrErrVR(subTy, desc)
		return r.toJSON(), r.detail

class ParseErrVR(InvalidVR):
	ty = 'ERR-PRSE'

	def __init__(self, subTy, isDriverErr, file, line, column, diagDesc, desc):
		super().__init__(subTy, isDriverErr, desc)
		self._file = file
		self._line = line
		self._column = column
		self._diagDesc = diagDesc

	@property
	def detail(self):
		return 'Compilation error: %s, in %s line %s column %s: %s %s\n%s' % ('DRIVER' if self._isDriverErr else 'CONFIG', self._file, self._line, self._column, self._subTy, self._diagDesc, self._desc)

	@property
	def diagDesc(self):
		return self._diagDesc

	@property
	def taxon(self):
		return '-'.join([ self.ty, 'DRIVER' if self._isDriverErr else 'CONFIG', self._subTy, self._desc ])

	def toJSON(self):
		return {'ty': self.ty, '_subTy': self._subTy, '_desc': self._desc, '_isDriverErr': self._isDriverErr, '_diagDesc': self._diagDesc, '_file': self._file, '_line': self._line, '_column': self._column}

	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty:
			return ParseErrVR(jsonobj['_subTy'], jsonobj['_isDriverErr'], jsonobj['_file'], jsonobj['_line'], jsonobj['_column'], jsonobj['_diagDesc'], jsonobj['_desc'])
		else:
			raise Exception('wrong ty %s' % (jsonobj['ty']))

	@classmethod
	def build(cls, diag, driverPath):
		# it is driver's error if the compilation fails in the driver file
		r = ParseErrVR(diag.category_name, str(diag.location.file) == str(driverPath), str(diag.location.file), str(diag.location.line), str(diag.location.column), str(diag), diag.spelling)
		return r.toJSON(), r.detail

#
# collected from source code of binutils-gdb/ld
#
linkPtrns = {
	"""undefined reference to `(.*)'\n""" : "UNDEF-REF",
	"""undefined reference to `(.*)',""" : "UNDEF-REF",
	"""undefined reference to `(.*)'\b""" : "UNDEF-REF",
	"""undefined reference to symbol '(.*)'""" : "UNDEF-REF",
	"""ld.lld: error: undefined symbol: (.*)\n""" : "UNDEF-REF",
	"""error: no such file or directory: '(.*)'""" : "NO-FILE-DIR",
}

class LinkErrVR(InvalidVR):
	ty = 'ERR-LINK'

	def __init__(self, subTy, reference, desc):
		super().__init__(subTy, False, desc)
		self._reference = reference

	@property
	def detail(self):
		return 'Linkage error: %s %s %s\n%s' % ('CONFIG', self._subTy, self._reference, self._desc)

	@property
	def taxon(self):
		return '-'.join([ self.ty, 'DRIVER' if self._isDriverErr else 'CONFIG', self._subTy, self._reference ])

	def toJSON(self):
		return {'ty': self.ty, '_subTy': self._subTy, '_desc': self._desc, '_isDriverErr': self._isDriverErr, '_reference': self._reference}

	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty:
			return LinkErrVR(jsonobj['_subTy'], jsonobj['_reference'], jsonobj['_desc'])
		else:
			raise Exception('wrong ty %s' % (jsonobj['ty']))

	@classmethod
	def build(cls, desc):
		r, match, subty, reference = None, None, 'UNKNOWN', desc.split('\n')[0]
		for ptrn, _subty in linkPtrns.items():
			match = re.search(ptrn, desc)
			if match != None:
				subty = _subty
				#print(desc)
				#print(match.groups())
				#print(ptrn)
				reference = match.groups()[0]
				break

		r = LinkErrVR(subty, reference, desc)

		return r.toJSON(), r.detail

asanPtrn = """ERROR: AddressSanitizer: (.*)\n"""
asanOracleGroups = {
	"""ASAN-attempting double-free on""" : """ASAN-attempting double-free on XXX""",
	"""ASAN-heap-buffer-overflow on address""" : """ASAN-heap-buffer-overflow on address XXX""",
	"""ASAN-heap-use-after-free on address""" : """ASAN-heap-use-after-free on address XXX""",
	"""ASAN-stack-buffer-overflow on address""" : """ASAN-stack-buffer-overflow on address XXX""",
	"""ASAN-stack-buffer-underflow on address""" : """ASAN-stack-buffer-underflow on address XXX""",
	"""ASAN-stack-overflow on address""" : """ASAN-stack-overflow on address XXX""",
	"""ASAN-global-buffer-overflow on address""" : """ASAN-global-buffer-overflow on address XXX""",
	"""ASAN-SEGV on unknown address""" : """ASAN-SEGV on unknown address XXX""",
	"""ASAN-dynamic-stack-buffer-overflow on address""" : """ASAN-dynamic-stack-buffer-overflow on address XXX""",
	"""ASAN-invalid alignment requested in posix_memalign:""" : """ASAN-invalid alignment requested in posix_memalign: XXX""",
	"""ASAN-FPE on unknown address""" : """ASAN-FPE on unknown address XXX""",
	"""ASAN-requested allocation size""" : """ASAN-requested allocation size XXX""",
	"""ASAN-attempting free on address which was not malloc()-ed:""" : """ASAN-attempting free on address which was not malloc()-ed: XXX""",
	"""ASAN-memcpy-param-overlap:""" : """ASAN-memcpy-param-overlap: XXX""",
	"""ASAN-stack-use-after-scope on address""" : """ASAN-stack-use-after-scope on address XXX""",
	"""ASAN-negative-size-param:""" : """ASAN-negative-size-param: XXX""",
	"""ASAN-unknown-crash on address""" : """ASAN-unknown-crash on address XXX""",
	"""ASAN-calloc parameters overflow: count * size""" : """ASAN-calloc parameters overflow: count * size XXX""",
}

# semantic error based on the oracles manually built from the specific API usage
class SemaErrVR(InvalidVR):
	ty = 'ERR-SEMA'

	def __init__(self, subTy, desc):
		super().__init__(subTy, True, desc)
	
	@property
	def detail(self):
		return 'Semantic error: %s %s\n%s' % ('DRIVER', self._subTy, self._desc)

	@property
	def taxon(self):
		return '-'.join([ self.ty, 'DRIVER', self._subTy ])

	def toJSON(self):
		return {'ty': self.ty, '_subTy': self._subTy, '_desc': self._desc, '_isDriverErr': self._isDriverErr}
	
	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty:
			return SemaErrVR(jsonobj['_subTy'], jsonobj['_desc'])
		else:
			raise Exception('wrong ty %s' % (jsonobj['ty']))
	
	@classmethod
	def build(cls, subty, desc):
		r = SemaErrVR(subty, desc)

		return r.toJSON(), r.detail
	
libFuzzerPtrn = """ERROR: libFuzzer: (.*)\n"""
libFuzzerOracleGroups = {
	"""libFuzzer-timeout after """ : """libFuzzer-timeout after XXX""",
}

def represents_int(s):
    try: 
        int(s)
    except ValueError:
        return False
    else:
        return True

class FuzzErrVR(InvalidVR):
	ty = 'ERR-FUZZ'

	def __init__(self, subTy, oracle, stacks, round, desc):
		super().__init__(subTy, True, desc)
		self._oracle = oracle
		# stacks contains a list of a list of stack frames (can have multiple stacks)
		self._stacks = stacks
		self._round = round

	@property
	def detail(self):
		#return 'Fuzz error: %s %s %s\n%s' % ('DRIVER', self._subTy, self._oracle, self._desc)
		return 'Fuzz error: %s %s %s with at least %s rounds\nIdentified stacks:\n%s\n%s' % ('DRIVER', self._subTy, self._oracle, self._round, self._stacks, self._desc)

	def oracleGrouping(self):
		global asanOracleGroups, libFuzzerOracleGroups

		if self._oracle.startswith('ASAN-'):
			for k, v in asanOracleGroups.items():
				if self._oracle.startswith(k):
					return v
		
		elif self._oracle.startswith('libFuzzer-'):
			for k, v in libFuzzerOracleGroups.items():
				if self._oracle.startswith(k):
					return v

		return self._oracle

	@property
	def taxon(self):
		return '-'.join([ self.ty, 'DRIVER' if self._isDriverErr else 'CONFIG', self._subTy, self.oracleGrouping() ])

	def toJSON(self):
		return {'ty': self.ty, '_subTy': self._subTy, '_desc': self._desc, '_isDriverErr': self._isDriverErr, '_stacks': self._stacks, '_round': self._round, '_oracle': self._oracle}

	@classmethod
	def load(cls, jsonobj):
		if jsonobj['ty'] == cls.ty:
			return FuzzErrVR(jsonobj['_subTy'], jsonobj['_oracle'], jsonobj['_stacks'], jsonobj['_round'], jsonobj['_desc'])
		else:
			raise Exception('wrong ty %s' % (jsonobj['ty']))

	@classmethod
	def parseStacks(cls, fuzzlog):
		lines = fuzzlog.split('\n')
		# stacks are continuous lines that starts with '#'
		stacks = []

		stack = []
		for i in range(len(lines)):
			raw_line = lines[i]
			line = raw_line.strip()

			if not raw_line.startswith('#'):
				if line.startswith('#'):
					stack.append(line)
					continue

			if len(stack) > 0:
				stacks.append(stack)
				stack = []

		if len(stack) > 0:
			stacks.append(stack)

		return stacks

	@classmethod
	def build(cls, subTy, oracle, stacks, round, desc):
		r = FuzzErrVR(subTy, oracle, stacks, round, desc)
		return r.toJSON(), r.detail

	@staticmethod
	def fn_check(fn_conds, fuzzlog):
		for fn_cond in fn_conds:
			all_match = True
			
			for partial_cond in fn_cond:
				if partial_cond not in fuzzlog:
					all_match = False
					break

			if all_match:
				return True
		
		return False

	@staticmethod
	def analyze_fuzz_result(ret, logfile, fn_conds):
		'''
		return FuzzErrVR or ValidVR
		'''
		global asanPtrn, libFuzzerPtrn

		subTy = 'RET-%s' % (ret)
		try:
			with open(logfile, 'rb') as f:
				raw_fuzzlog = None
				try:
					raw_fuzzlog = f.read(-1)

				except MemoryError as me:
					return FuzzErrVR.build(subTy, 'CORR-LOG', [], None, 'log file corrupted with memory error')

				fuzzlog = raw_fuzzlog.decode('utf-8', errors='ignore')
				stacks = FuzzErrVR.parseStacks(fuzzlog)

				lines = fuzzlog.split('\n')
				initline, doneline, round = None, None, None
				for line in lines:
					if line.startswith('#'):
						# parse line starting with #int to get round
						roundstr = None
						for idx in range(len(line)):
							if line[idx].isspace():
								roundstr = line[1:idx]
								break

						if represents_int(roundstr):
							round = int(roundstr)

							if 'INITED' in line:
								initline = line
							elif 'DONE' in line:
								doneline = line

				fn_detected = FuzzErrVR.fn_check(fn_conds, fuzzlog)
				if fn_detected:
					return PartlyCheckedVR.build('Fuzz check has passed with FN detected\n' + fuzzlog)

				elif 'LeakSanitizer: detected memory leaks' in fuzzlog:
					# memory leak
					return FuzzErrVR.build(subTy, 'MEMLEAK', stacks, round, fuzzlog)
				elif 'out-of-memory' in fuzzlog:
					# oom
					return FuzzErrVR.build(subTy, 'OOM', stacks, round, fuzzlog)
				elif ret != 0:
					# asan
					match = re.search(asanPtrn, fuzzlog)
					if match != None:
						oracle = 'ASAN-%s' % (match.groups()[0])
						return FuzzErrVR.build(subTy, oracle, stacks, round, fuzzlog)

					# libFuzzer
					match = re.search(libFuzzerPtrn, fuzzlog)
					if match != None:
						oracle = 'libFuzzer-%s' % (match.groups()[0])
						return FuzzErrVR.build(subTy, oracle, stacks, round, fuzzlog)

					# unknown
					return FuzzErrVR.build(subTy, 'UNKNOWN', stacks, round, fuzzlog)
				else:
					# ret == 0
					if initline == None or doneline == None:
						return FuzzErrVR.build(subTy, 'NOINIT-LOG', stacks, round, fuzzlog)

					initcov = int(initline.split('cov: ')[1].split(' ft:')[0])
					donecov = int(doneline.split('cov: ')[1].split(' ft:')[0])
					if initcov == donecov:
						return FuzzErrVR.build(subTy, 'NONEFF', stacks, round, fuzzlog)
					else:
						return PartlyCheckedVR.build('Fuzz check has passed\n' + fuzzlog)

		except Exception as ex:
			return FuzzErrVR.build(subTy, 'UNK-EXP', [], None, str(ex))
