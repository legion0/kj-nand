import sys, re
import string, cStringIO
import token, tokenize
from collections import namedtuple

Token = namedtuple("Token", ["type", "value", "srow", "scol", "erow", "ecol", "line"])

TOK_STRING = token.STRING

tmp_tok = token.NT_OFFSET + 1
TOK_KEYWORD = tmp_tok
token.tok_name[tmp_tok] = "KEYWORD"
tmp_tok += 1
TOK_SYMBOL = tmp_tok
token.tok_name[tmp_tok] = "SYMBOL"
tmp_tok += 1
TOK_INTEGER = tmp_tok
token.tok_name[tmp_tok] = "INTEGER"
tmp_tok += 1
TOK_IDENTIFIER = tmp_tok
token.tok_name[tmp_tok] = "IDENTIFIER"
del tmp_tok
_TOKENS = (TOK_KEYWORD, TOK_SYMBOL, TOK_INTEGER, TOK_IDENTIFIER, TOK_STRING)

def newTokenizor(source):
	return Lookahead(Parser(source).parse())

_KEYWORDS = (
	"class",
	"constructor",
	"function",
	"method",
	"field",
	"static",
	"var",
	"int",
	"char",
	"boolean",
	"void",
	"true",
	"false",
	"null",
	"this",
	"let",
	"do",
	"if",
	"else",
	"while",
	"return",
)

_SYMBOLS = (
	"{",
	"}",
	"(",
	")",
	"[",
	"]",
	".",
	",",
	";",
	"+",
	"-",
	"*",
	"/",
	"&",
	"|",
	"<",
	">",
	"=",
	"~",
)

class Lookahead:
	def __init__(self, iter_):
		self.iter = iter_
		self.buffer = []

	def __iter__(self):
		return self

	def next(self):
		if self.buffer:
			return self.buffer.pop(0)
		else:
			return self.iter.next()

	def lookahead(self, n = 0):
		while n >= len(self.buffer):
			try:
				self.buffer.append(self.iter.next())
			except StopIteration:
				return None
		return self.buffer[n]

class Parser:

	def __init__(self, raw, out = sys.stdout):
		self.raw = string.strip(string.expandtabs(raw))
		self.out = out
		self.inComment = False
		self.commentType = None
		self.commentText = None
		self.possibleMultilineComment = False
		self.possibleMultilineChar = None
		self.backupMode = False
		self.tok = None
		self.nextTok = None

	def parse(self):
		self.lines = [0, 0]
		pos = 0
		while 1:
			pos = string.find(self.raw, '\n', pos) + 1
			if not pos: break
			self.lines.append(pos)
		self.lines.append(len(self.raw))

		self.pos = 0
		text = cStringIO.StringIO(self.raw)
		self.iter = Lookahead(tokenize.generate_tokens(text.readline))
		self.next()
		try:
			while self.tok is not None:
				self.skipJunk()
				self.processToken()
				tok = self.tok
				yield Token(tok[0], tok[1], tok[2][0], tok[2][1], tok[3][0], tok[3][1], tok[4])
				self.next()
		except tokenize.TokenError, ex:
			msg = ex[0]
			line = ex[1][0]
			self.out.write("ERROR: %s %s\n" % (
				msg, self.raw[self.lines[line]:]))

	def next(self, jump = 1):
		for _ in xrange(jump):
			self.tok = self.iter.next()
			self.nextTok = self.iter.lookahead()

	def skipComments(self):
		junk = False
		if self.tok[0] == token.OP and self.tok[1] == "//":
			junk = True
			while self.tok[0] not in (token.NEWLINE, tokenize.NL):
				self.next()
			self.next()
		if self.tok[0] == token.OP and self.tok[1] == "/" and self.nextTok[0] == token.OP and self.nextTok[1] in ("*", "**"):
			junk = True
			while not (self.tok[0] == token.OP and self.tok[1] in ("*", "**") and self.nextTok[0] == token.OP and self.nextTok[1] == "/"):
				self.next()
			self.next(2)
		return junk

	def skipJunk(self):
		if self.skipComments() or self.skipMisc():
			self.skipJunk()

	def skipMisc(self):
		junk = False
		while self.tok[0] in (tokenize.NL, token.INDENT, token.DEDENT, token.NEWLINE, token.ENDMARKER):
			self.next()
			junk = True
		return junk

	def processToken(self):
		toktype, toktext, (srow,scol), (erow,ecol), line = self.tok
		self.tok = list(self.tok)
		if toktype == token.NAME:
			if toktext in _KEYWORDS:
				toktype = TOK_KEYWORD
			elif re.match(r"^[a-z_][a-z_0-9]*$", toktext, re.IGNORECASE) is not None:
				toktype = TOK_IDENTIFIER
			else:
				raise SyntaxError("Unknown Keyword/Identifier %s" % toktext, (None, srow, scol, line))
		if toktype == token.OP:
			if toktext not in _SYMBOLS:
				raise SyntaxError("Unknown Symbol %s" % toktext, (None, srow, scol, line))
			toktype = TOK_SYMBOL
		if toktype == token.NUMBER:
			if re.match(r"^\d+$", toktext, re.IGNORECASE) is None:
				raise SyntaxError("Unknown Expression %s" % toktext, (None, srow, scol, line))
			toktype = TOK_INTEGER
		if toktype not in _TOKENS: # misc illegal tokens
			raise SyntaxError("Unknown Expression %s" % toktext, (None, srow, scol, line))
		if toktype == token.STRING:
			toktext = toktext[1:-1]
		self.tok = (toktype, toktext, (srow,scol), (erow,ecol), line)
		return
