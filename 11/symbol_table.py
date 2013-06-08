class SymbolTable:

	def __init__(self):
		self.big_table = {}
		self.small_table = {}
		self.big_index = _EMPTY_INDEX.copy()
		self.small_index = _EMPTY_INDEX.copy()

	def startSubroutine(self, className, methodName):
		self.small_table = {}
		self.small_index = _EMPTY_INDEX.copy()

	def define(self, name, type_, kind):
		if kind not in KINDS.ALL:
			raise RuntimeError("kind %r not in list" % kind)
		index = None
		if kind in KINDS.BIG_SCOPE:
			if name not in self.big_table:
				index = self.big_index[kind]
				self.big_table[name] = (type_, kind, index)
				self.big_index[kind] = index + 1
		elif kind in KINDS.SMALL_SCOPE:
			if name not in self.small_table:
				index = self.small_index[kind]
				self.small_table[name] = (type_, kind, index)
				self.small_index[kind] = index + 1
		return index

	def varCount(self, kind):
		if kind in KINDS.BIG_SCOPE:
			return len([1 for _, x in self.big_table.viewitems() if x[1] == kind])
		elif kind in KINDS.SMALL_SCOPE:
			return len([1 for _, x in self.small_table.viewitems() if x[1] == kind])
		return 0

	def kindOf(self, name):
		if name in self.big_table:
			return self.big_table[name][1]
		elif name in self.small_table:
			return self.small_table[name][1]
		return None

	def typeOf(self, name):
		if name in self.big_table:
			return self.big_table[name][0]
		elif name in self.small_table:
			return self.small_table[name][0]
		return None

	def indexOf(self, name):
		if name in self.big_table:
			return self.big_table[name][2]
		elif name in self.small_table:
			return self.small_table[name][2]
		return None

class KINDS:
	STATIC = "STATIC"
	FIELD = "FIELD"
	ARG = "ARG"
	VAR = "VAR"
	ALL = (STATIC, FIELD, ARG, VAR)
	SMALL_SCOPE = (VAR, ARG)
	BIG_SCOPE = (STATIC, FIELD)

_EMPTY_INDEX = {
	KINDS.STATIC: 0,
	KINDS.FIELD: 0,
	KINDS.ARG: 0,
	KINDS.VAR: 0,
}