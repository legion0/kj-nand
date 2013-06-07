

from compilation import ELEMENTS
from symbol_table import KINDS

class SEGMENT:
	CONST = 1
	ARG = 2
	LOCAL = 3
	STATIC = 4
	THIS = 5
	THAT = 6
	POINTER = 7
	TEMP = 8
	ALL = (CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP)

_SEGMENTS = {
	SEGMENT.CONST: "constant",
	SEGMENT.ARG: "argument",
	SEGMENT.LOCAL: "local",
	SEGMENT.STATIC: "static",
	SEGMENT.THIS: "this",
	SEGMENT.THAT: "that",
	SEGMENT.POINTER: "pointer",
	SEGMENT.TEMP: "temp",
}

_SYM_TRANSLATE = {
	"+": "add",
	"*": "call Math.multiply 2",
	"-": "sub",
}
_SYM_TRANSLATE_UNARY = {
	"-": "neg",
	"~": "not",
}

class COMMAND:
	ADD = 1
	SUB = 2
	NEG = 3
	EQ = 4
	GT = 5
	LT = 6
	AND = 7
	OR = 8
	NOT = 9
	ALL = (ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT)

_COMMANDS = {
	COMMAND.ADD: "None",
	COMMAND.SUB: None,
	COMMAND.NEG: None,
	COMMAND.EQ: None,
	COMMAND.GT: None,
	COMMAND.LT: None,
	COMMAND.AND: None,
	COMMAND.OR: None,
	COMMAND.NOT: None,
}

_SEGMENT_MAP = {
	KINDS.ARG: SEGMENT.ARG,
	KINDS.FIELD: SEGMENT.THIS,
	KINDS.STATIC: SEGMENT.STATIC,
	KINDS.VAR: SEGMENT.LOCAL,
}

class VMWriter:
	def __init__(self, out):
		self.out = out
		self.statement_writers = {
			"letStatement": self._write_letStatement,
			"ifStatement": self._write_ifStatement,
			"whileStatement": self._write_whileStatement,
			"doStatement": self._write_doStatement,
			"returnStatement": self._write_returnStatement,
		}

	def writePush(self, segment, index):
		if segment not in _SEGMENTS:
			raise ValueError("Illegal segment: %s" % segment)
		self.out.write("push %s %s\n" % (_SEGMENTS[segment], index))

	def writePop(self, segment, index):
		if segment not in _SEGMENTS:
			raise ValueError("Illegal segment: %s" % segment)
		self.out.write("pop %s %s\n" % (_SEGMENTS[segment], index))

	def writeArithmetic(self, command):
		self.out.write("%s\n" % (command))

	def writeLabel(self, label):
		self.out.write("label %s\n" % (label))

	def writeGoto(self, label):
		self.out.write("goto %s\n" % (label))

	def writeIf(self, label):
		self.out.write("if-goto %s\n" % (label))

	def writeCall(self, name, nArgs):
		self.out.write("call %s %s\n" % (name, nArgs))

	def writeFunction(self, name, nLocals):
		self.out.write("function %s %s\n" % (name, nLocals))

	def writeReturn(self):
		self.out.write("return\n")

	def writeXml(self, root):
		self.className = root[1].text
		for element in root:
			if element.tag == ELEMENTS.SUBROUTINEDEC:
				self._write_subroutineDec(element)

	def _write_subroutineDec(self, root):
		name = root[2].text
		body = root.find(ELEMENTS.SUBROUTINEBODY)
		nLocals = 0
		for local in body.findall(ELEMENTS.VAR_DEC):
			nLocals += (len(local) - 2) / 2
		self.writeFunction("%s.%s" % (self.className, name), nLocals)
		self._write_statements(body.find(ELEMENTS.STATEMENTS))

	def _write_statements(self, root):
		for element in root:
			self.statement_writers[element.tag](element)

	def _write_letStatement(self, root):
		self._write_expression(root.find(ELEMENTS.EXPRESSION))
		self.writePop(*get_var_info(root[1]))
	def _write_ifStatement(self, root):
		pass
	def _write_whileStatement(self, root):
		pass
	def _write_doStatement(self, root):
		expList = root.find(ELEMENTS.EXPRESSION_LIST)
		for exp in expList.findall(ELEMENTS.EXPRESSION):
			self._write_expression(exp)
		fName = "%s.%s" % (root[1].text, root[3].text)
		nArgs = len(expList.findall(ELEMENTS.EXPRESSION))
		self.writeCall(fName, nArgs)
	def _write_returnStatement(self, root):
		if len(root) == 2:
			self.writeReturn()

	def _write_expression(self, root):
		self._write_term(root[0])
		for i in xrange(2, len(root), 2):
			self._write_term(root[i])
			self._write_symbol(root[i-1])

	def _write_term(self, root):
		if root[0].tag == ELEMENTS.INTEGER_CONSTANT:
			self.writePush(SEGMENT.CONST, root[0].text)
		elif root[0].text in _SYM_TRANSLATE_UNARY:
			self._write_term(root[1])
			self.writeArithmetic(_SYM_TRANSLATE_UNARY[root[0].text])
		elif is_object_call(root):
			expList = root.find(ELEMENTS.EXPRESSION_LIST)
			self._write_expression_list(expList)
			fName = "%s.%s" % (root[0].text, root[2].text)
			nArgs = len(expList.findall(ELEMENTS.EXPRESSION))
			self.writeCall(fName, nArgs)
		elif root[0].text == "(":
			self._write_expression(root[1])
		elif len(root) == 1 and root[0].tag == ELEMENTS.IDENTIFIER:
			self.writePush(*get_var_info(root[0]))
		elif len(root) == 1 and root[0].tag == ELEMENTS.KEYWORD and root[0].text in ("true", "false"):
			if root[0].text == "true":
				self.writePush(SEGMENT.CONST, "0")
			else:
				self.writePush(SEGMENT.CONST, "1")
				self.writeArithmetic("neg")
	def _write_expression_list(self, root):
		for element in root.findall(ELEMENTS.EXPRESSION):
			self._write_expression(element)

	def _write_symbol(self, root):
		self.writeArithmetic(_SYM_TRANSLATE[root.text])

def is_object_call(root):
	return len(root) >= 6 and root[0].tag == ELEMENTS.IDENTIFIER and root[1].tag == ELEMENTS.SYMBOL and root[2].tag == ELEMENTS.IDENTIFIER

def get_var_info(root):
	return _SEGMENT_MAP[int(root.get("kind"))], root.get("index")