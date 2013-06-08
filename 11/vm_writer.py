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
	"/": "call Math.divide 2",
	"&": "and",
	"|": "or",
	"<": "lt",
	">": "gt",
	"=": "eq",
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

class VMWriter:
	def __init__(self, out):
		self.out = out

	def writePush(self, segment, index):
		self.out.write("push %s %s\n" % (_SEGMENTS[segment], index))

	def writePop(self, segment, index):
		self.out.write("pop %s %s\n" % (_SEGMENTS[segment], index))

	def writeArithmetic(self, command):
		command = _SYM_TRANSLATE.get(command, command)
		self.out.write("%s\n" % (command))

	def writeArithmeticUnary(self, command):
		command = _SYM_TRANSLATE_UNARY.get(command, command)
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
