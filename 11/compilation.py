from xml.etree.ElementTree import Element, tostring
from xml.dom.minidom import parseString, Document
from collections import namedtuple

import tokenizor
from tokenizor import newTokenizor
from symbol_table import SymbolTable, KINDS as SYM_KINDS
from vm_writer import VMWriter

#TODO: remove
import json

class _ELEMENTS:
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

class _KEYWORDS:
	VAR = "var"
	ELSE = "else"
	CONSTANT_TRUE = "true"
	CONSTANT_FALSE = "false"
	CONSTANT_NULL = "null"
	CONSTANT_THIS = "this"
	CONSTANTS = (CONSTANT_FALSE, CONSTANT_NULL, CONSTANT_THIS, CONSTANT_TRUE)

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

_SYM_ART_MAP = {
	"+": "ADD",
	"+": "ADD",
	"+": "ADD",
	"+": "ADD",
	"+": "ADD",
	"+": "ADD",
	"+": "ADD",
}

class _CLASSVARDEC:
	FIELD_TYPES = ("static", "field")
	VAR_TYPES = ("int", "char", "boolean")

class _SUBROUTINEDEC:
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
		self.iter = newTokenizor(self.src)
		self.doc = Document()
		self._symbol_table = SymbolTable()

	def compile(self):
		root = self._compileClass()
   		self.writer.writeXml(root)
#    		parseString(tostring(root)).documentElement.writexml(self.dst, addindent="\t", newl="\n")

	def _compileClass(self):
		classE = Element(_ELEMENTS.CLASS)
		self._readKeyword(classE, _ELEMENTS.CLASS)
		self._readIdentifier(classE)
		self._readSymbol(classE, _SYMBOLS.BRACKET_CURLY_OPEN)
		self._compileClassVarDec(classE)
		self._compileSubroutine(classE)
		self._readSymbol(classE, _SYMBOLS.BRACKET_CURLY_CLOSE)
		return classE

	def _compileClassVarDec(self, parent):
		while self.nextTok.type == tokenizor.TOK_KEYWORD and self.nextTok.value in _CLASSVARDEC.FIELD_TYPES:
			classVarDecE = Element(_ELEMENTS.CLASSVARDEC)
			self._readKeyword(classVarDecE)
			self._readType(classVarDecE)
			self._readIdentifier(classVarDecE)
			while self._readSymbolOptional(classVarDecE, _SYMBOLS.COMMA):
				self._readIdentifier(classVarDecE)
			self._readSymbol(classVarDecE, _SYMBOLS.SEMI_COLON)
			parent.append(classVarDecE)

	def _compileSubroutine(self, parent):
		while self.nextTok.type == tokenizor.TOK_KEYWORD and self.nextTok.value in _SUBROUTINEDEC.TYPES:
			self._symbol_table.startSubroutine()
			subroutineDecE = Element(_ELEMENTS.SUBROUTINEDEC)
			self._readKeyword(subroutineDecE)
			self._readReturnType(subroutineDecE)
			self._readIdentifier(subroutineDecE)
			self._readSymbol(subroutineDecE, _SYMBOLS.PARENTHESES_OPEN)
			self._compileParameters(subroutineDecE)
			self._readSymbol(subroutineDecE, _SYMBOLS.PARENTHESES_CLOSE)
			self._compileSubroutineBody(subroutineDecE)
			parent.append(subroutineDecE)

	def _compileSubroutineBody(self, parent):
		bodyE = Element(_ELEMENTS.SUBROUTINEBODY)
		self._readSymbol(bodyE, _SYMBOLS.BRACKET_CURLY_OPEN)
		self._compileVarDec(bodyE)
		self._compileStatements(bodyE)
		self._readSymbol(bodyE, _SYMBOLS.BRACKET_CURLY_CLOSE)
		parent.append(bodyE)

	def _compileStatements(self, parent):
		statementsE = Element(_ELEMENTS.STATEMENTS)
		while self.nextTok.type == tokenizor.TOK_KEYWORD and self.nextTok.value in _STATEMENTS.TYPE_NAMES:
			if self.nextTok.value == _STATEMENTS.LET:
				statementE = Element(_ELEMENTS.STATEMENT_LET)
				self._readKeyword(statementE)
				self._readIdentifier(statementE)
				if self._readSymbolOptional(statementE, _SYMBOLS.BRACKET_OPEN):
					self._compileExpression(statementE)
					self._readSymbol(statementE, _SYMBOLS.BRACKET_CLOSE)
				self._readSymbol(statementE, _SYMBOLS.EQUAL)
				self._compileExpression(statementE)
				self._readSymbol(statementE, _SYMBOLS.SEMI_COLON)
				statementsE.append(statementE)
			elif self.nextTok.value == _STATEMENTS.IF:
				statementE = Element(_ELEMENTS.STATEMENT_IF)
				self._readKeyword(statementE)
				self._readSymbol(statementE, _SYMBOLS.PARENTHESES_OPEN)
				self._compileExpression(statementE)
				self._readSymbol(statementE, _SYMBOLS.PARENTHESES_CLOSE)
				self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_OPEN)
				self._compileStatements(statementE)
				self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_CLOSE)
				if self._readKeywordOptional(statementE, _KEYWORDS.ELSE):
					self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_OPEN)
					self._compileStatements(statementE)
					self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_CLOSE)
				statementsE.append(statementE)
			elif self.nextTok.value == _STATEMENTS.WHILE:
				statementE = Element(_ELEMENTS.STATEMENT_WHILE)
				self._readKeyword(statementE)
				self._readSymbol(statementE, _SYMBOLS.PARENTHESES_OPEN)
				self._compileExpression(statementE)
				self._readSymbol(statementE, _SYMBOLS.PARENTHESES_CLOSE)
				self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_OPEN)
				self._compileStatements(statementE)
				self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_CLOSE)
				statementsE.append(statementE)
			elif self.nextTok.value == _STATEMENTS.DO:
				self._compileDo(statementsE)
			elif self.nextTok.value == _STATEMENTS.RETURN:
				statementE = Element(_ELEMENTS.STATEMENT_RETURN)
				self._readKeyword(statementE)
				if not (self.nextTok.type == tokenizor.TOK_SYMBOL and self.nextTok.value == _SYMBOLS.SEMI_COLON):
					self._compileExpression(statementE)
				self._readSymbol(statementE, _SYMBOLS.SEMI_COLON)
				statementsE.append(statementE)
		if len(statementsE) == 0:
			statementsE.text = "\n"
		parent.append(statementsE)

	def _compileExpression(self, parent):
		expressionE = Element(_ELEMENTS.EXPRESSION)
		self._readTerm(expressionE)
		while self.nextTok.type == tokenizor.TOK_SYMBOL and self.nextTok.value in _SYMBOLS.OPERATORS:
			self._readSymbol(expressionE)
			self._readTerm(expressionE)
		parent.append(expressionE)

	def _compileExpressionList(self, parent):
		self._readSymbol(parent, _SYMBOLS.PARENTHESES_OPEN)
		expListE = Element(_ELEMENTS.EXPRESSION_LIST)
		while not (self.nextTok.type == tokenizor.TOK_SYMBOL and self.nextTok.value == _SYMBOLS.PARENTHESES_CLOSE):
			self._compileExpression(expListE)
			self._readSymbolOptional(expListE, _SYMBOLS.COMMA)
		# hack for TextComparer
		if len(expListE) == 0:
			expListE.text = "\n"
		parent.append(expListE)
		self._readSymbol(parent, _SYMBOLS.PARENTHESES_CLOSE)

	def _compileDo(self, parent):
		statementE = Element(_ELEMENTS.STATEMENT_DO)
		self._readKeyword(statementE, _STATEMENTS.DO)
		self._readIdentifier(statementE)
		if self._readSymbolOptional(statementE, _SYMBOLS.DOT):
			self._readIdentifier(statementE)
		self._compileExpressionList(statementE)
		self._readSymbol(statementE, _SYMBOLS.SEMI_COLON)
		parent.append(statementE)

	def _compileVarDec(self, parent):
		while self.nextTok.type == tokenizor.TOK_KEYWORD and self.nextTok.value == _KEYWORDS.VAR:
			varDecE = Element(_ELEMENTS.VAR_DEC)
			self._readKeyword(varDecE, _KEYWORDS.VAR)
			self._readType(varDecE)
			self._readIdentifier(varDecE)
			while self._readSymbolOptional(varDecE, _SYMBOLS.COMMA):
				self._readIdentifier(varDecE)
			self._readSymbol(varDecE, _SYMBOLS.SEMI_COLON)
			parent.append(varDecE)

	def _compileParameters(self, parent):
		paramListE = Element(_ELEMENTS.PARAM_LIST)
		while (self.nextTok.type == tokenizor.TOK_KEYWORD and self.nextTok.value in _CLASSVARDEC.VAR_TYPES) or self.nextTok.type == tokenizor.TOK_IDENTIFIER:
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
		termE = Element(_ELEMENTS.TERM)
		if self.nextTok.type == tokenizor.TOK_INTEGER:
			self.next()
			termE.append(_leafElement(_ELEMENTS.INTEGER_CONSTANT, self.tok.value))
		elif self.nextTok.type == tokenizor.TOK_STRING:
			self.next()
			termE.append(_leafElement(_ELEMENTS.STRING_CONSTANT, self.tok.value))
		elif self.nextTok.type == tokenizor.TOK_KEYWORD and self.nextTok.value in _KEYWORDS.CONSTANTS:
			self.next()
			termE.append(_leafElement(_ELEMENTS.KEYWORD, self.tok.value))
		elif self.nextTok.type == tokenizor.TOK_IDENTIFIER:
			self._readIdentifier(termE)
			if self._readSymbolOptional(termE, _SYMBOLS.BRACKET_OPEN):
				self._compileExpression(termE)
				self._readSymbol(termE, _SYMBOLS.BRACKET_CLOSE)
			elif self.nextTok.type == tokenizor.TOK_SYMBOL and self.nextTok.value == _SYMBOLS.PARENTHESES_OPEN:
				self._compileExpressionList(termE)
				self._readSymbol(termE, _SYMBOLS.PARENTHESES_CLOSE)
			elif self._readSymbolOptional(termE, _SYMBOLS.DOT):
				self._readIdentifier(termE)
				self._compileExpressionList(termE)
		elif self.nextTok.type == tokenizor.TOK_SYMBOL and self.nextTok.value == _SYMBOLS.PARENTHESES_OPEN:
			self.next()
			termE.append(_leafElement(_ELEMENTS.SYMBOL, self.tok.value))
			self._compileExpression(termE)
			self._readSymbol(termE, _SYMBOLS.PARENTHESES_CLOSE)
		elif self.nextTok.type == tokenizor.TOK_SYMBOL and self.nextTok.value in _SYMBOLS.UNARY_OPARTORS:
			self.next()
			termE.append(_leafElement(_ELEMENTS.SYMBOL, self.tok.value))
			self._readTerm(termE)
		else:
			raise self._syntaxError("Unexpected %s." % self.tok.value)
		parent.append(termE)

	def _readIdentifier(self, parent):
		self.next()
		self._assertToken(self.tok, _ELEMENTS.IDENTIFIER, type_=tokenizor.TOK_IDENTIFIER)
		name = self.tok.value
		element = _leafElement(_ELEMENTS.IDENTIFIER, name)
		type_ = None
		kind = None
		index = None
		if self._symbol_table.typeOf(name) is None:
			if parent.tag in (_ELEMENTS.CLASSVARDEC, _ELEMENTS.VAR_DEC) and len(parent) > 1:
				type_ = parent[1].text
				kind = _SYM_KIND_MAP[parent[0].text]
			elif parent.tag == _ELEMENTS.PARAM_LIST:
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

	def _readType(self, parent):
		if self.nextTok.type == tokenizor.TOK_KEYWORD and self.nextTok.value in _CLASSVARDEC.VAR_TYPES:
			self.next()
			parent.append(_leafElement(_ELEMENTS.KEYWORD, self.tok.value))
		else:
			self._readIdentifier(parent)

	def _readReturnType(self, parent):
		if self.nextTok.type == tokenizor.TOK_KEYWORD and self.nextTok.value in _SUBROUTINEDEC.RETURN_TYPES:
			self.next()
			parent.append(_leafElement(_ELEMENTS.KEYWORD, self.tok.value))
		else:
			self._readIdentifier(parent)

	def _readSymbol(self, parent, expected = None):
		self.next()
		expectedStr = expected if expected is not None else _ELEMENTS.SYMBOL
		self._assertToken(self.tok, expectedStr, type_=tokenizor.TOK_SYMBOL)
		if expected is not None:
			self._assertToken(self.tok, expected, value_=expected)
		parent.append(_leafElement(_ELEMENTS.SYMBOL, self.tok.value))

	def _readKeyword(self, parent, expected = None):
		self.next()
		expectedStr = expected if expected is not None else _ELEMENTS.KEYWORD
		self._assertToken(self.tok, expectedStr, type_=tokenizor.TOK_KEYWORD)
		if expected is not None:
			self._assertToken(self.tok, expected, value_=expected)
		parent.append(_leafElement(_ELEMENTS.KEYWORD, self.tok.value))

	def _readSymbolOptional(self, parent, expected):
		if self.nextTok.type == tokenizor.TOK_SYMBOL and self.nextTok.value == expected:
			self.next()
			parent.append(_leafElement(_ELEMENTS.SYMBOL, self.tok.value))
			return True
		return False

	def _readKeywordOptional(self, parent, expected):
		if self.nextTok.type == tokenizor.TOK_KEYWORD and self.nextTok.value == expected:
			self.next()
			parent.append(_leafElement(_ELEMENTS.KEYWORD, self.tok.value))
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
