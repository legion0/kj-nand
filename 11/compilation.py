from xml.etree.ElementTree import Element

import tokenizor
from symbol_table import SymbolTable, KINDS as SYM_KINDS
from vm_writer import VMWriter, SEGMENT
from scanner import Lookahead

class ELEMENTS:
	CLASS = "class"
	KEYWORD = "keyword"
	IDENTIFIER = "identifier"
	CLASSVARDEC = "classVarDec"
	SYMBOL = "symbol"
	PARAM_LIST = "parameterList"
	SUBROUTINEDEC = "subroutineDec"
	SUBROUTINEBODY = "subroutineBody"
	VAR_DEC = "varDec"
	STATEMENTS = "statements"
	STATEMENT_LET = "letStatement"
	STATEMENT_RETURN = "returnStatement"
	STATEMENT_DO = "doStatement"
	STATEMENT_IF = "ifStatement"
	STATEMENT_WHILE = "whileStatement"
	EXPRESSION_LIST = "expressionList"
	EXPRESSION = "expression"
	INTEGER_CONSTANT = "integerConstant"
	STRING_CONSTANT = "stringConstant"
	KEYWORD_CONSTANT = "keywordConstant"
	TERM = "term"

_SEG_TRANSLATE = {
	SYM_KINDS.STATIC: SEGMENT.STATIC,
	SYM_KINDS.FIELD: SEGMENT.THIS,
	SYM_KINDS.ARG: SEGMENT.ARG,
	SYM_KINDS.VAR: SEGMENT.LOCAL,
}

class _KEYWORDS:
	VAR = "var"
	ELSE = "else"
	CONSTANT_TRUE = "true"
	CONSTANT_FALSE = "false"
	CONSTANT_NULL = "null"
	CONSTANT_THIS = "this"
	CONSTANTS = (CONSTANT_FALSE, CONSTANT_NULL, CONSTANT_THIS, CONSTANT_TRUE)

_KW_CONT_WRITE = {
	_KEYWORDS.CONSTANT_TRUE: lambda writer: writer.writePush(SEGMENT.CONST, "0") or  writer.writeArithmetic("not"),
	_KEYWORDS.CONSTANT_FALSE: lambda writer: writer.writePush(SEGMENT.CONST, "0"),
	_KEYWORDS.CONSTANT_NULL: lambda writer: writer.writePush(SEGMENT.CONST, "0"),
	_KEYWORDS.CONSTANT_THIS: lambda writer: writer.writePush(SEGMENT.POINTER, "0"),
}

class _SYMBOLS:
	BRACKET_OPEN = "["
	BRACKET_CLOSE = "]"
	BRACKET_CURLY_OPEN = "{"
	BRACKET_CURLY_CLOSE = "}"
	PARENTHESES_OPEN = "("
	PARENTHESES_CLOSE = ")"
	SEMI_COLON = ";"
	COMMA = ","
	EQUAL = "="
	DOT = "."
	OPERATORS = ("+", "-", "*", "/", "&", "|", "<", ">", "=")
	UNARY_OPARTORS = ("-", "~")

class _CLASSVARDEC:
	FIELD_TYPES = ("static", "field")
	VAR_TYPES = ("int", "char", "boolean")

class _SUBROUTINEDEC:
	CONSTRUCTOR = "constructor"
	FUNCTION = "function"
	METHOD = "method"
	TYPES = ("constructor", "function", "method")
	RETURN_TYPES = _CLASSVARDEC.VAR_TYPES[:] + ("void",)

class _STATEMENTS:
	LET = "let"
	IF = "if"
	WHILE = "while"
	DO = "do"
	RETURN = "return"
	TYPE_NAMES = (LET, IF, WHILE, DO, RETURN)

_SYM_KIND_MAP = {
	"field": SYM_KINDS.FIELD,
	"static": SYM_KINDS.STATIC,
	"var": SYM_KINDS.VAR,
}

def _leafElement(tag, text):
	elem = Element(tag)
	elem.text = "%s" % text
	return elem

class CompilationEngine:
	def __init__(self, source, destination):
		self.src = source
		self.dst = destination
		self.writer = VMWriter(destination)
		self.iter = Lookahead(tokenizor.newTokenizor(self.src))
		self._symbol_table = SymbolTable()

	def compile(self):
		root = self._compileClass()
		return root

	def _compileClass(self):
		classE = Element(ELEMENTS.CLASS)
		self._readKeyword(classE, ELEMENTS.CLASS)
		self.className = self._readIdentifier(classE)
		self._readSymbol(classE, _SYMBOLS.BRACKET_CURLY_OPEN)
		self._compileClassVarDec(classE)
		self._compileSubroutine(classE)
		self._readSymbol(classE, _SYMBOLS.BRACKET_CURLY_CLOSE)
		return classE

	def _compileClassVarDec(self, parent):
		while self.nextTok.type == tokenizor.KEYWORD and self.nextTok.value in _CLASSVARDEC.FIELD_TYPES:
			classVarDecE = Element(ELEMENTS.CLASSVARDEC)
			self._readKeyword(classVarDecE)
			self._readType(classVarDecE)
			self._readIdentifier(classVarDecE)
			while self._readSymbolOptional(classVarDecE, _SYMBOLS.COMMA):
				self._readIdentifier(classVarDecE)
			self._readSymbol(classVarDecE, _SYMBOLS.SEMI_COLON)
			parent.append(classVarDecE)

	def _compileSubroutine(self, parent):
		while self.nextTok and self.nextTok.type == tokenizor.KEYWORD and self.nextTok.value in _SUBROUTINEDEC.TYPES:
			subroutineDecE = Element(ELEMENTS.SUBROUTINEDEC)
			function_type = self._readKeyword(subroutineDecE)
			self._readReturnType(subroutineDecE)
			self.methodName = self._readIdentifier(subroutineDecE)
			self._symbol_table.startSubroutine(self.className, self.methodName)
			if function_type == _SUBROUTINEDEC.METHOD:
				self._symbol_table.define("this", self.className, SYM_KINDS.ARG)
			self._uid = -1
			self._readSymbol(subroutineDecE, _SYMBOLS.PARENTHESES_OPEN)
			self._compileParameters(subroutineDecE)
			self._readSymbol(subroutineDecE, _SYMBOLS.PARENTHESES_CLOSE)
			self._compileSubroutineBody(subroutineDecE, function_type)
			parent.append(subroutineDecE)

	def _gen_label(self, type_):
		self._uid += 1
		return "%s.%s.%s.%d" % (self.className, self.methodName, type_, self._uid)

	def _gen_labels(self, *parts):
		self._uid += 1
		return ["%s.%s.%s.%d" % (self.className, self.methodName, part, self._uid) for part in parts]

	def _compileSubroutineBody(self, parent, function_type):
		bodyE = Element(ELEMENTS.SUBROUTINEBODY)
		self._readSymbol(bodyE, _SYMBOLS.BRACKET_CURLY_OPEN)
		nArgs = self._compileVarDec(bodyE)
		function_name = parent[2].text
		function_full_name = "%s.%s" % (self.className, function_name)
		self.writer.writeFunction(function_full_name, nArgs)
		if function_type == _SUBROUTINEDEC.CONSTRUCTOR:
			field_count = self._symbol_table.varCount(SYM_KINDS.FIELD)
			self.writer.writePush(SEGMENT.CONST, field_count)
			self.writer.writeCall("Memory.alloc", 1)
			self.writer.writePop(SEGMENT.POINTER, 0)
		elif function_type == _SUBROUTINEDEC.METHOD:
			self.writer.writePush(SEGMENT.ARG, 0)
			self.writer.writePop(SEGMENT.POINTER, 0)
		self._compileStatements(bodyE)
		self._readSymbol(bodyE, _SYMBOLS.BRACKET_CURLY_CLOSE)
		parent.append(bodyE)

	def _compileStatements(self, parent):
		statementsE = Element(ELEMENTS.STATEMENTS)
		while self.nextTok.type == tokenizor.KEYWORD and self.nextTok.value in _STATEMENTS.TYPE_NAMES:
			if self.nextTok.value == _STATEMENTS.LET:
				statementE = Element(ELEMENTS.STATEMENT_LET)
				self._readKeyword(statementE)
				identifier = self._readIdentifier(statementE)
				is_array = False
				if self._readSymbolOptional(statementE, _SYMBOLS.BRACKET_OPEN):
					is_array = True
					self._compileExpression(statementE)
					self.writer.writePush(*self._identifier_data(identifier))
					self.writer.writeArithmetic("add")
					self._readSymbol(statementE, _SYMBOLS.BRACKET_CLOSE)
				self._readSymbol(statementE, _SYMBOLS.EQUAL)
				self._compileExpression(statementE)
				self._readSymbol(statementE, _SYMBOLS.SEMI_COLON)
				if is_array:
					self.writer.writePop(SEGMENT.TEMP, 0)
					self.writer.writePop(SEGMENT.POINTER, 1)
					self.writer.writePush(SEGMENT.TEMP, 0)
					self.writer.writePop(SEGMENT.THAT, 0)
				else:
					self.writer.writePop(*self._identifier_data(identifier))
				statementsE.append(statementE)
			elif self.nextTok.value == _STATEMENTS.IF:
				label_else, label_end = self._gen_labels("if.else", "if.end")
				statementE = Element(ELEMENTS.STATEMENT_IF)
				self._readKeyword(statementE)
				self._readSymbol(statementE, _SYMBOLS.PARENTHESES_OPEN)
				self._compileExpression(statementE)
				self._readSymbol(statementE, _SYMBOLS.PARENTHESES_CLOSE)
				self.writer.writeArithmetic("not")
				self.writer.writeIf(label_else)
				self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_OPEN)
				self._compileStatements(statementE)
				self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_CLOSE)
				self.writer.writeGoto(label_end)
				self.writer.writeLabel(label_else)
				if self._readKeywordOptional(statementE, _KEYWORDS.ELSE):
					self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_OPEN)
					self._compileStatements(statementE)
					self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_CLOSE)
				self.writer.writeLabel(label_end)
				statementsE.append(statementE)
			elif self.nextTok.value == _STATEMENTS.WHILE:
				label_start, label_end = self._gen_labels("while.start", "while.end")
				self.writer.writeLabel(label_start)
				statementE = Element(ELEMENTS.STATEMENT_WHILE)
				self._readKeyword(statementE)
				self._readSymbol(statementE, _SYMBOLS.PARENTHESES_OPEN)
				self._compileExpression(statementE)
				self._readSymbol(statementE, _SYMBOLS.PARENTHESES_CLOSE)
				self.writer.writeArithmetic("not")
				self.writer.writeIf(label_end)
				self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_OPEN)
				self._compileStatements(statementE)
				self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_CLOSE)
				statementsE.append(statementE)
				self.writer.writeGoto(label_start)
				self.writer.writeLabel(label_end)
			elif self.nextTok.value == _STATEMENTS.DO:
				self._compileDo(statementsE)
			elif self.nextTok.value == _STATEMENTS.RETURN:
				statementE = Element(ELEMENTS.STATEMENT_RETURN)
				self._readKeyword(statementE)
				if not (self.nextTok.type == tokenizor.SYMBOL and self.nextTok.value == _SYMBOLS.SEMI_COLON):
					self._compileExpression(statementE)
				else:
					self.writer.writePush(SEGMENT.CONST, 0)
				self._readSymbol(statementE, _SYMBOLS.SEMI_COLON)
				self.writer.writeReturn()
				statementsE.append(statementE)
		if len(statementsE) == 0:
			statementsE.text = "\n"
		parent.append(statementsE)

	def _compileExpression(self, parent):
		expressionE = Element(ELEMENTS.EXPRESSION)
		self._readTerm(expressionE)
		while self.nextTok.type == tokenizor.SYMBOL and self.nextTok.value in _SYMBOLS.OPERATORS:
			symbol = self._readSymbol(expressionE)
			self._readTerm(expressionE)
			self.writer.writeArithmetic(symbol)
		parent.append(expressionE)

	def _compileExpressionList(self, parent):
		self._readSymbol(parent, _SYMBOLS.PARENTHESES_OPEN)
		expListE = Element(ELEMENTS.EXPRESSION_LIST)
		nArgs = 0
		while not (self.nextTok.type == tokenizor.SYMBOL and self.nextTok.value == _SYMBOLS.PARENTHESES_CLOSE):
			self._compileExpression(expListE)
			self._readSymbolOptional(expListE, _SYMBOLS.COMMA)
			nArgs += 1
		# hack for TextComparer
		if len(expListE) == 0:
			expListE.text = "\n"
		parent.append(expListE)
		self._readSymbol(parent, _SYMBOLS.PARENTHESES_CLOSE)
		return nArgs

	def _compileDo(self, parent):
		statementE = Element(ELEMENTS.STATEMENT_DO)
		self._readKeyword(statementE, _STATEMENTS.DO)
		identifier = self._readIdentifier(statementE)
		nArgs = 0
		if self._readSymbolOptional(statementE, _SYMBOLS.DOT):
			type_ = self._symbol_table.typeOf(identifier)
			if type_:
				segment, index = self._identifier_data(identifier)
				self.writer.writePush(segment, index)
				nArgs += 1
				identifier = "%s.%s" % (type_, self._readIdentifier(statementE))
			else:
				identifier = "%s.%s" % (identifier, self._readIdentifier(statementE))
		else:
			identifier = "%s.%s" % (self.className, identifier)
			self.writer.writePush(SEGMENT.POINTER, 0)
			nArgs += 1
		nArgs += self._compileExpressionList(statementE)
		self._readSymbol(statementE, _SYMBOLS.SEMI_COLON)
		self.writer.writeCall(identifier, nArgs)
		self.writer.writePop(SEGMENT.TEMP, 0)
		parent.append(statementE)

	def _compileVarDec(self, parent):
		nArgs = 0
		while self.nextTok.type == tokenizor.KEYWORD and self.nextTok.value == _KEYWORDS.VAR:
			varDecE = Element(ELEMENTS.VAR_DEC)
			self._readKeyword(varDecE, _KEYWORDS.VAR)
			self._readType(varDecE)
			self._readIdentifier(varDecE)
			nArgs += 1
			while self._readSymbolOptional(varDecE, _SYMBOLS.COMMA):
				self._readIdentifier(varDecE)
				nArgs += 1
			self._readSymbol(varDecE, _SYMBOLS.SEMI_COLON)
			parent.append(varDecE)
		return nArgs

	def _compileParameters(self, parent):
		paramListE = Element(ELEMENTS.PARAM_LIST)
		while (self.nextTok.type == tokenizor.KEYWORD and self.nextTok.value in _CLASSVARDEC.VAR_TYPES) or self.nextTok.type == tokenizor.IDENTIFIER:
			self._readType(paramListE)
			self._readIdentifier(paramListE)
			self._readSymbolOptional(paramListE, _SYMBOLS.COMMA)
		if len(paramListE) == 0:
			paramListE.text = "\n"
		parent.append(paramListE)

##############################
########## READ ##############
##############################

	def _readTerm(self, parent):
		termE = Element(ELEMENTS.TERM)
		if self.nextTok.type == tokenizor.INTEGER:
			self.next()
			termE.append(_leafElement(ELEMENTS.INTEGER_CONSTANT, self.tok.value))
			self.writer.writePush(SEGMENT.CONST, self.tok.value)
		elif self.nextTok.type == tokenizor.STRING:
			self.next()
			termE.append(_leafElement(ELEMENTS.STRING_CONSTANT, self.tok.value))
			string_value = self.tok.value
			self.writer.writePush(SEGMENT.CONST, len(string_value))
			self.writer.writeCall("String.new", 1)
			for char in string_value:
				self.writer.writePush(SEGMENT.CONST, ord(char))
				self.writer.writeCall("String.appendChar", 2)
		elif self.nextTok.type == tokenizor.KEYWORD and self.nextTok.value in _KEYWORDS.CONSTANTS:
			self.next()
			termE.append(_leafElement(ELEMENTS.KEYWORD, self.tok.value))
			_KW_CONT_WRITE[self.tok.value](self.writer)
		elif self.nextTok.type == tokenizor.IDENTIFIER:
			identifier = self._readIdentifier(termE)
			nArgs = 0
			if self._readSymbolOptional(termE, _SYMBOLS.BRACKET_OPEN):
				self._compileExpression(termE)
				self.writer.writePush(*self._identifier_data(identifier))
				self.writer.writeArithmetic("add")
				self.writer.writePop(SEGMENT.POINTER, 1)
				self.writer.writePush(SEGMENT.THAT, 0)
				self._readSymbol(termE, _SYMBOLS.BRACKET_CLOSE)
			elif self.nextTok.type == tokenizor.SYMBOL and self.nextTok.value == _SYMBOLS.PARENTHESES_OPEN:
				nArgs = self._compileExpressionList(termE)
				self._readSymbol(termE, _SYMBOLS.PARENTHESES_CLOSE)
				self.writer.writeCall(identifier, nArgs)
			elif self._readSymbolOptional(termE, _SYMBOLS.DOT):
				type_ = self._symbol_table.typeOf(identifier)
				if type_:
					segment, index = self._identifier_data(identifier)
					self.writer.writePush(segment, index)
					nArgs += 1
					identifier = "%s.%s" % (type_, self._readIdentifier(termE))
				else:
					identifier = "%s.%s" % (identifier, self._readIdentifier(termE))
				nArgs += self._compileExpressionList(termE)
				self.writer.writeCall(identifier, nArgs)
			else:
				self.writer.writePush(*self._identifier_data(identifier))
		elif self.nextTok.type == tokenizor.SYMBOL and self.nextTok.value == _SYMBOLS.PARENTHESES_OPEN:
			self.next()
			termE.append(_leafElement(ELEMENTS.SYMBOL, self.tok.value))
			self._compileExpression(termE)
			self._readSymbol(termE, _SYMBOLS.PARENTHESES_CLOSE)
		elif self.nextTok.type == tokenizor.SYMBOL and self.nextTok.value in _SYMBOLS.UNARY_OPARTORS:
			self.next()
			sym = self.tok.value
			termE.append(_leafElement(ELEMENTS.SYMBOL, self.tok.value))
			self._readTerm(termE)
			self.writer.writeArithmeticUnary(sym)
		else:
			raise self._syntaxError("Unexpected %s." % self.tok.value)
		parent.append(termE)

	def _identifier_data(self, identifier):
		return _SEG_TRANSLATE[self._symbol_table.kindOf(identifier)], self._symbol_table.indexOf(identifier)

	def _readIdentifier(self, parent):
		self.next()
		self._assertToken(self.tok, ELEMENTS.IDENTIFIER, type_=tokenizor.IDENTIFIER)
		name = self.tok.value
		element = _leafElement(ELEMENTS.IDENTIFIER, name)
		type_ = self._symbol_table.typeOf(name)
		kind = None
		index = None
		if type_ is None:
			if parent.tag in (ELEMENTS.CLASSVARDEC, ELEMENTS.VAR_DEC) and len(parent) > 1:
				type_ = parent[1].text
				kind = _SYM_KIND_MAP[parent[0].text]
			elif parent.tag == ELEMENTS.PARAM_LIST and len(parent) > 0:
				type_ = parent[-1].text
				kind = SYM_KINDS.ARG
			if kind is not None:
				index = self._symbol_table.define(name, type_, kind)
		else:
			type_ = self._symbol_table.typeOf(name)
			kind = self._symbol_table.kindOf(name)
			index = self._symbol_table.indexOf(name)
		if kind is not None:
			element.set("type", type_)
			element.set("kind", str(kind))
			element.set("index", str(index))
		parent.append(element)
		return name

	def _readType(self, parent):
		if self.nextTok.type == tokenizor.KEYWORD and self.nextTok.value in _CLASSVARDEC.VAR_TYPES:
			self.next()
			parent.append(_leafElement(ELEMENTS.KEYWORD, self.tok.value))
		else:
			self._readIdentifier(parent)

	def _readReturnType(self, parent):
		if self.nextTok.type == tokenizor.KEYWORD and self.nextTok.value in _SUBROUTINEDEC.RETURN_TYPES:
			self.next()
			parent.append(_leafElement(ELEMENTS.KEYWORD, self.tok.value))
		else:
			self._readIdentifier(parent)

	def _readSymbol(self, parent, expected = None):
		self.next()
		expectedStr = expected if expected is not None else ELEMENTS.SYMBOL
		self._assertToken(self.tok, expectedStr, type_=tokenizor.SYMBOL)
		if expected is not None:
			self._assertToken(self.tok, expected, value_=expected)
		parent.append(_leafElement(ELEMENTS.SYMBOL, self.tok.value))
		return self.tok.value

	def _readKeyword(self, parent, expected = None):
		self.next()
		expectedStr = expected if expected is not None else ELEMENTS.KEYWORD
		self._assertToken(self.tok, expectedStr, type_=tokenizor.KEYWORD)
		if expected is not None:
			self._assertToken(self.tok, expected, value_=expected)
		parent.append(_leafElement(ELEMENTS.KEYWORD, self.tok.value))
		return self.tok.value

	def _readSymbolOptional(self, parent, expected):
		if self.nextTok.type == tokenizor.SYMBOL and self.nextTok.value == expected:
			self.next()
			parent.append(_leafElement(ELEMENTS.SYMBOL, self.tok.value))
			return True
		return False

	def _readKeywordOptional(self, parent, expected):
		if self.nextTok.type == tokenizor.KEYWORD and self.nextTok.value == expected:
			self.next()
			parent.append(_leafElement(ELEMENTS.KEYWORD, self.tok.value))
			return True
		return False

	def next(self):
		self.tok = self.iter.next()
		self.nextTok = self.iter.lookahead()

	def _assertToken(self, tok, expected_str, type_ = None, value_ = None):
		if (type_ != None and tok.type != type_) or (value_ != None and tok.value != value_):
			raise self._syntaxError("Expected %s but found %s" % (expected_str, tok.value), tok)

	def _syntaxError(self, msg, tok = None):
		if tok is None:
			tok = self.tok
		return SyntaxError(msg, (None, tok.srow, tok.scol, tok.line))
