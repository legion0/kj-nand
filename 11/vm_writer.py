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
	SEGMENT.CONST: None,
	SEGMENT.ARG: None,
	SEGMENT.LOCAL: None,
	SEGMENT.STATIC: None,
	SEGMENT.THIS: None,
	SEGMENT.THAT: None,
	SEGMENT.POINTER: None,
	SEGMENT.TEMP: None,
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
	COMMAND.ADD: None,
	COMMAND.SUB: None,
	COMMAND.NEG: None,
	COMMAND.EQ: None,
	COMMAND.GT: None,
	COMMAND.LT: None,
	COMMAND.AND: None,
	COMMAND.OR: None,
	COMMAND.NOT: None,
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
		self.out.write("push %s %s\n" % (segment, index))

	def writePop(self, segment, index):
		self.out.write("pop %s %s\n" % (segment, index))

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
			if element.tag == "subroutineDec":
				self._write_subroutineDec(element)

	def _write_subroutineDec(self, root):
		name = root[2].text
		body = root.find("subroutineBody")
		nLocals = len(body.findall("varDec"))
		self.writeFunction("%s.%s" % (self.className, name), nLocals)
		self._write_statements(body.find("statements"))

	def _write_statements(self, root):
		for element in root:
			self.statement_writers[element.tag](element)
	
	def _write_letStatement(self, root):
		pass
	def _write_ifStatement(self, root):
		pass
	def _write_whileStatement(self, root):
		pass
	def _write_doStatement(self, root):
		pass
	def _write_returnStatement(self, root):
		pass
			
			
			
			
			
			
			
			