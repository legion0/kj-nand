# TODO: remove this
import json

class SymbolTable:
	
	def __init__(self):
		self.big_table = {}
		self.big_index = 0
		self.startSubroutine()

	def startSubroutine(self):
		self.small_table = {}
		self.small_index = 0

	def define(self, name, type_, kind):
		if kind not in KINDS.ALL:
			raise RuntimeError("kind %r not in list" % kind)
		index = None
		if kind in KINDS.BIG_SCOPE:
			if name not in self.big_table:
				self.big_table[name] = (type_, kind, self.big_index)
				index = self.big_index
				self.big_index+=1
		elif kind in KINDS.SMALL_SCOPE:
			if name not in self.small_table:
				self.small_table[name] = (type_, kind, self.small_index)
				index = self.small_index
				self.small_index+=1
		return index

	def varCount(self, kind):
		if kind in KINDS.BIG_SCOPE:
			return len([1 for x in self.big_table if x[1] == kind])
		elif kind in KINDS.SMALL_SCOPE:
			return len([1 for x in self.small_table if x[1] == kind])
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

	def dump(self): # TODO: remove this
# 		print json.dumps(self.big_table, indent=4)
# 		print json.dumps(self.small_table, indent=4)
		pass

class KINDS:
	STATIC = 1
	FIELD = 2
	ARG = 3
	VAR = 4
	ALL = (STATIC, FIELD, ARG, VAR)
	SMALL_SCOPE = (VAR, ARG)
	BIG_SCOPE = (STATIC, FIELD)