from xml.etree.ElementTree import Element, tostring
from xml.dom.minidom import parseString, Document

import tokenizor
from tokenizor import newTokenizor

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

def _leafElement(tag, text):
	elem = Element(tag)
	elem.text = "%s" % text
	return elem

class CompilationEngine:
	def __init__(self, source, destination):
		self.src = source
		self.dst = destination
		self.iter = newTokenizor(self.src)
		self.doc = Document()

	def compile(self):
		root = self._compileClass()
		parseString(tostring(root)).documentElement.writexml(self.dst, addindent="\t", newl="\n")

	def _compileClass(self):
		tok = self.iter.next()
		self._assertToken(tok, _ELEMENTS.CLASS, value_=_ELEMENTS.CLASS)
		classE = Element(_ELEMENTS.CLASS)
		classE.append(_leafElement(_ELEMENTS.KEYWORD, _ELEMENTS.CLASS))
		tok = self.iter.next()
		self._assertToken(tok, _ELEMENTS.IDENTIFIER, type_=tokenizor.TOK_IDENTIFIER)
		classE.append(_leafElement(_ELEMENTS.IDENTIFIER, tok.value))
		self._readSymbol(classE, _SYMBOLS.BRACKET_CURLY_OPEN)
		self._compileClassVarDec(classE)
		self._compileSubroutine(classE)
		self._readSymbol(classE, _SYMBOLS.BRACKET_CURLY_CLOSE)
		return classE

	def _compileClassVarDec(self, parent):
		tok = self.iter.lookahead()
		while tok.type == tokenizor.TOK_KEYWORD and tok.value in _CLASSVARDEC.FIELD_TYPES:
			classVarDecE = Element(_ELEMENTS.CLASSVARDEC)
			tok = self.iter.next()
			classVarDecE.append(_leafElement(_ELEMENTS.KEYWORD, tok.value))
			self._readType(classVarDecE)
			self._readIdentifier(classVarDecE)
			while self._readSymbolOptional(classVarDecE, _SYMBOLS.COMMA):
				self._readIdentifier(classVarDecE)
			self._readSymbol(classVarDecE, _SYMBOLS.SEMI_COLON)
			parent.append(classVarDecE)
			tok = self.iter.lookahead()

	def _compileSubroutine(self, parent):
		tok = self.iter.lookahead()
		while tok.type == tokenizor.TOK_KEYWORD and tok.value in _SUBROUTINEDEC.TYPES:
			subroutineDecE = Element(_ELEMENTS.SUBROUTINEDEC)
			tok = self.iter.next()
			subroutineDecE.append(_leafElement(_ELEMENTS.KEYWORD, tok.value))
			self._readReturnType(subroutineDecE)
			self._readIdentifier(subroutineDecE)
			self._readSymbol(subroutineDecE, _SYMBOLS.PARENTHESES_OPEN)
			self._readParameters(subroutineDecE)
			self._readSymbol(subroutineDecE, _SYMBOLS.PARENTHESES_CLOSE)
			self._compileSubroutineBody(subroutineDecE)
			parent.append(subroutineDecE)
			tok = self.iter.lookahead()

	def _compileSubroutineBody(self, parent):
		bodyE = Element(_ELEMENTS.SUBROUTINEBODY)
		self._readSymbol(bodyE, _SYMBOLS.BRACKET_CURLY_OPEN)
		self._compileVarDec(bodyE)
		self._compileStatements(bodyE)
		self._readSymbol(bodyE, _SYMBOLS.BRACKET_CURLY_CLOSE)
		parent.append(bodyE)

	def _compileStatements(self, parent):
		statementsE = Element(_ELEMENTS.STATEMENTS)
		tok = self.iter.lookahead()
		while tok.type == tokenizor.TOK_KEYWORD and tok.value in _STATEMENTS.TYPE_NAMES:
			tok = self.iter.next()
			if tok.value == _STATEMENTS.LET:
				statementE = Element(_ELEMENTS.STATEMENT_LET)
				statementE.append(_leafElement(_ELEMENTS.KEYWORD, tok.value))
				self._readIdentifier(statementE)
				if self._readSymbolOptional(statementE, _SYMBOLS.BRACKET_OPEN):
					self._compileExpression(statementE)
					self._readSymbol(statementE, _SYMBOLS.BRACKET_CLOSE)
				self._readSymbol(statementE, _SYMBOLS.EQUAL)
				self._compileExpression(statementE)
				self._readSymbol(statementE, _SYMBOLS.SEMI_COLON)
				statementsE.append(statementE)
			elif tok.value == _STATEMENTS.IF:
				statementE = Element(_ELEMENTS.STATEMENT_IF)
				statementE.append(_leafElement(_ELEMENTS.KEYWORD, tok.value))
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
			elif tok.value == _STATEMENTS.WHILE:
				statementE = Element(_ELEMENTS.STATEMENT_WHILE)
				statementE.append(_leafElement(_ELEMENTS.KEYWORD, tok.value))
				self._readSymbol(statementE, _SYMBOLS.PARENTHESES_OPEN)
				self._compileExpression(statementE)
				self._readSymbol(statementE, _SYMBOLS.PARENTHESES_CLOSE)
				self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_OPEN)
				self._compileStatements(statementE)
				self._readSymbol(statementE, _SYMBOLS.BRACKET_CURLY_CLOSE)
				statementsE.append(statementE)
			elif tok.value == _STATEMENTS.DO:
				self._compileDo(statementsE)
			elif tok.value == _STATEMENTS.RETURN:
				statementE = Element(_ELEMENTS.STATEMENT_RETURN)
				statementE.append(_leafElement(_ELEMENTS.KEYWORD, tok.value))
				tok = self.iter.lookahead()
				if not (tok.type == tokenizor.TOK_SYMBOL and tok.value == _SYMBOLS.SEMI_COLON):
					self._compileExpression(statementE)
				self._readSymbol(statementE, _SYMBOLS.SEMI_COLON)
				statementsE.append(statementE)
			tok = self.iter.lookahead()
		if len(statementsE) == 0:
			statementsE.text = "\n"
		parent.append(statementsE)

	def _compileExpression(self, parent):
		expressionE = Element(_ELEMENTS.EXPRESSION)
		self._readTerm(expressionE)
		tok = self.iter.lookahead()
		while tok.type == tokenizor.TOK_SYMBOL and tok.value in _SYMBOLS.OPERATORS:
			self._readSymbol(expressionE)
			self._readTerm(expressionE)
			tok = self.iter.lookahead()
		parent.append(expressionE)

	def _readTerm(self, parent):
		tok = self.iter.next()
		termE = Element(_ELEMENTS.TERM)
		if tok.type == tokenizor.TOK_INTEGER:
			termE.append(_leafElement(_ELEMENTS.INTEGER_CONSTANT, tok.value))
		elif tok.type == tokenizor.TOK_STRING:
			termE.append(_leafElement(_ELEMENTS.STRING_CONSTANT, tok.value))
		elif tok.type == tokenizor.TOK_KEYWORD and tok.value in _KEYWORDS.CONSTANTS:
			termE.append(_leafElement(_ELEMENTS.KEYWORD, tok.value))
		elif tok.type == tokenizor.TOK_IDENTIFIER:
			termE.append(_leafElement(_ELEMENTS.IDENTIFIER, tok.value))
			tok = self.iter.lookahead()
			if self._readSymbolOptional(termE, _SYMBOLS.BRACKET_OPEN):
				self._compileExpression(termE)
				self._readSymbol(termE, _SYMBOLS.BRACKET_CLOSE)
			elif tok.type == tokenizor.TOK_SYMBOL and tok.value == _SYMBOLS.PARENTHESES_OPEN:
				self._compileExpressionList(termE)
				self._readSymbol(termE, _SYMBOLS.PARENTHESES_CLOSE)
			elif self._readSymbolOptional(termE, _SYMBOLS.DOT):
				self._readIdentifier(termE)
				self._compileExpressionList(termE)
		elif tok.type == tokenizor.TOK_SYMBOL and tok.value == _SYMBOLS.PARENTHESES_OPEN:
			termE.append(_leafElement(_ELEMENTS.SYMBOL, tok.value))
			self._compileExpression(termE)
			self._readSymbol(termE, _SYMBOLS.PARENTHESES_CLOSE)
		elif tok.type == tokenizor.TOK_SYMBOL and tok.value in _SYMBOLS.UNARY_OPARTORS:
			termE.append(_leafElement(_ELEMENTS.SYMBOL, tok.value))
			self._readTerm(termE)
		else:
			raise self._syntaxError("Unexpected %s." % tok.value, tok)
		parent.append(termE)

	def _compileExpressionList(self, parent):
		self._readSymbol(parent, _SYMBOLS.PARENTHESES_OPEN)
		expListE = Element(_ELEMENTS.EXPRESSION_LIST)
		tok = self.iter.lookahead()
		while not (tok.type == tokenizor.TOK_SYMBOL and tok.value == _SYMBOLS.PARENTHESES_CLOSE):
			self._compileExpression(expListE)
			self._readSymbolOptional(expListE, _SYMBOLS.COMMA)
			tok = self.iter.lookahead()
		# hack for TextComparer
		if len(expListE) == 0:
			expListE.text = "\n"
		parent.append(expListE)
		self._readSymbol(parent, _SYMBOLS.PARENTHESES_CLOSE)

	def _compileDo(self, parent):
		statementE = Element(_ELEMENTS.STATEMENT_DO)
		statementE.append(_leafElement(_ELEMENTS.KEYWORD, _STATEMENTS.DO))
		self._readIdentifier(statementE)
		if self._readSymbolOptional(statementE, _SYMBOLS.DOT):
			self._readIdentifier(statementE)
		self._compileExpressionList(statementE)
		self._readSymbol(statementE, _SYMBOLS.SEMI_COLON)
		parent.append(statementE)

	def _compileVarDec(self, parent):
		tok = self.iter.lookahead()
		while tok.type == tokenizor.TOK_KEYWORD and tok.value == _KEYWORDS.VAR:
			tok = self.iter.next()
			varDecE = Element(_ELEMENTS.VAR_DEC)
			varDecE.append(_leafElement(_ELEMENTS.KEYWORD, _KEYWORDS.VAR))
			self._readType(varDecE)
			self._readIdentifier(varDecE)
			while self._readSymbolOptional(varDecE, _SYMBOLS.COMMA):
				self._readIdentifier(varDecE)
			self._readSymbol(varDecE, _SYMBOLS.SEMI_COLON)
			parent.append(varDecE)
			tok = self.iter.lookahead()

	def _readParameters(self, parent):
		tok = self.iter.lookahead()
		paramListE = Element(_ELEMENTS.PARAM_LIST)
		while (tok.type == tokenizor.TOK_KEYWORD and tok.value in _CLASSVARDEC.VAR_TYPES) or tok.type == tokenizor.TOK_IDENTIFIER:
			self._readType(paramListE)
			self._readIdentifier(paramListE)
			self._readSymbolOptional(paramListE, _SYMBOLS.COMMA)
			tok = self.iter.lookahead()
		if len(paramListE) == 0:
			paramListE.text = "\n"
		parent.append(paramListE)

	def _readIdentifier(self, parent):
		tok = self.iter.next()
		self._assertToken(tok, _ELEMENTS.IDENTIFIER, type_=tokenizor.TOK_IDENTIFIER)
		parent.append(_leafElement(_ELEMENTS.IDENTIFIER, tok.value))

	def _readType(self, parent):
		tok = self.iter.next()
		if tok.type == tokenizor.TOK_KEYWORD and tok.value in _CLASSVARDEC.VAR_TYPES:
			parent.append(_leafElement(_ELEMENTS.KEYWORD, tok.value))
		else:
			self._assertToken(tok, _ELEMENTS.IDENTIFIER, type_=tokenizor.TOK_IDENTIFIER)
			parent.append(_leafElement(_ELEMENTS.IDENTIFIER, tok.value))

	def _readReturnType(self, parent):
		tok = self.iter.next()
		if tok.type == tokenizor.TOK_KEYWORD and tok.value in _SUBROUTINEDEC.RETURN_TYPES:
			parent.append(_leafElement(_ELEMENTS.KEYWORD, tok.value))
		else:
			self._assertToken(tok, _ELEMENTS.IDENTIFIER, type_=tokenizor.TOK_IDENTIFIER)
			parent.append(_leafElement(_ELEMENTS.IDENTIFIER, tok.value))

	def _readSymbol(self, parent, expected = None):
		tok = self.iter.next()
		expectedStr = expected if expected is not None else _ELEMENTS.SYMBOL
		self._assertToken(tok, expectedStr, type_=tokenizor.TOK_SYMBOL)
		if expected is not None:
			self._assertToken(tok, expected, value_=expected)
		parent.append(_leafElement(_ELEMENTS.SYMBOL, tok.value))

	def _readSymbolOptional(self, parent, expected):
		tok = self.iter.lookahead()
		if tok.type == tokenizor.TOK_SYMBOL and tok.value == expected:
			self.iter.next()
			parent.append(_leafElement(_ELEMENTS.SYMBOL, tok.value))
			return True
		return False

	def _readKeywordOptional(self, parent, expected):
		tok = self.iter.lookahead()
		if tok.type == tokenizor.TOK_KEYWORD and tok.value == expected:
			self.iter.next()
			parent.append(_leafElement(_ELEMENTS.KEYWORD, tok.value))
			return True
		return False

	def _assertToken(self, tok, expected_str, type_ = None, value_ = None):
		if (type_ != None and tok.type != type_) or (value_ != None and tok.value != value_):
			raise self._syntaxError("Expected %s but found %s" % (expected_str, tok.value), tok)

	def _syntaxError(self, msg, tok):
		return SyntaxError(msg, (None, tok.srow, tok.scol, tok.line))
