## {{{ http://code.activestate.com/recipes/52298/ (r3)
"""
	MoinMoin - Python Source Parser
"""

# Imports
import sys, re
import string, cStringIO
import token, tokenize
from collections import namedtuple



#############################################################################
### Python Source Parser (does Hilighting)
#############################################################################

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

def getTypeName(tok_type):
	return token.tok_name[tok_type]

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
		"""Return an item n entries ahead in the iteration."""
		while n >= len(self.buffer):
			try:
				self.buffer.append(self.iter.next())
			except StopIteration:
				return None
		return self.buffer[n]

Token = namedtuple("Token", ["type", "value", "srow", "scol", "erow", "ecol", "line"])

class Parser:
	""" Send colored python source.
	"""
	COMMENT_SINGLE = 1
	COMMENT_MULTI = 2

	def __init__(self, raw, out = sys.stdout):
		""" Store the source text.
		"""
		self.raw = string.strip(string.expandtabs(raw))
		self.out = out
		self.inComment = False
		self.commentType = None
		self.commentText = None
		self.possibleMultilineComment = False
		self.possibleMultilineChar = None
		self.backupMode = False

	def parse(self):
		""" Parse and send the colored source.
		"""
		# store line offsets in self.lines
		self.lines = [0, 0]
		pos = 0
		while 1:
			pos = string.find(self.raw, '\n', pos) + 1
			if not pos: break
			self.lines.append(pos)
		self.lines.append(len(self.raw))

		# parse the source and write it
		self.pos = 0
		text = cStringIO.StringIO(self.raw)
		try:
			for tok in tokenize.generate_tokens(text.readline):
				tok = self.nextToken(*tok)
				if tok is None:
					continue
				yield Token(tok[0], tok[1], tok[2][0], tok[2][1], tok[3][0], tok[3][1], tok[4])
		except tokenize.TokenError, ex:
			msg = ex[0]
			line = ex[1][0]
			self.out.write("ERROR: %s %s\n" % (
				msg, self.raw[self.lines[line]:]))

	def nextToken(self, toktype, toktext, (srow,scol), (erow,ecol), line):
		""" Token handler.
		"""
#  		if False:
#   			print "[%s(%d)] %s" % (token.tok_name[toktype], toktype, toktext)
# 			print "start", srow,scol, "end", erow,ecol, "line:", line
		###
		### HANDLE COMMENTS
		###
		if self.backupMode:
			self.backupMode = False
			return self.backup
		if self.inComment:
			if self.commentType == self.COMMENT_SINGLE:
				if toktype in (token.NEWLINE, tokenize.NL):
					self.inComment = False
			elif self.commentType == self.COMMENT_MULTI:
				if toktype == token.OP and toktext == "/" and self.backup[0] == token.OP and self.backup[1] in ("*", "**"):
					self.inComment = False
			self.backup = (toktype, toktext, (srow,scol), (erow,ecol), line)
			return
		if toktype == token.OP and toktext == "//":
			self.inComment = True
			self.commentType = self.COMMENT_SINGLE
			self.backup = (toktype, toktext, (srow,scol), (erow,ecol), line)
			return
		if self.possibleMultilineComment:
			self.possibleMultilineComment = False
			if toktype == token.OP and toktext in ("*", "**"):
				self.inComment = True
				self.commentType = self.COMMENT_MULTI
				self.backup = (toktype, toktext, (srow,scol), (erow,ecol), line)
				return
			self.backupMode = True
			tmp = self.backup
			self.backup = (toktype, toktext, (srow,scol), (erow,ecol), line)
			return tmp
		if toktype == token.OP and toktext == "/":
			self.possibleMultilineComment = True
			self.backup = (toktype, toktext, (srow,scol), (erow,ecol), line)
			return
		###
		###
		###
		
		# JUNK TOKENS
		if toktype in (tokenize.NL, token.INDENT, token.DEDENT, token.NEWLINE, token.ENDMARKER):
			self.backup = (toktype, toktext, (srow,scol), (erow,ecol), line)
			return
		
		###
		### VALIDATION
		###
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
		self.backup = (toktype, toktext, (srow,scol), (erow,ecol), line)
		return self.backup
