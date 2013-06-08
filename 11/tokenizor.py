import sys, re
import string
from collections import namedtuple

from scanner import newScanner, JUNK_PATTERN_ID, Lookahead

Token = namedtuple("Token", ["type", "value", "srow", "scol", "erow", "ecol", "line"])

SYMBOL = "SYMBOL"
KEYWORD = "KEYWORD"
IDENTIFIER = "IDENTIFIER"
INTEGER = "INTEGER"
STRING = "STRING"
_TOKENS = (KEYWORD, SYMBOL, INTEGER, IDENTIFIER, STRING)

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

_RE_SYM = "(?:" + "|".join([re.escape(x) for x in _SYMBOLS]) + ")"
_RE_KEYWORD = "(?:" + "|".join([re.escape(x) for x in _KEYWORDS]) + ")"
scanner = newScanner((
	(JUNK_PATTERN_ID, r"//.*\n"),
	(JUNK_PATTERN_ID, r"/\*.*?\*/", re.DOTALL),
	(JUNK_PATTERN_ID, r"\n"),
	(JUNK_PATTERN_ID, r" "),
	(KEYWORD, _RE_KEYWORD),
	(SYMBOL, _RE_SYM),
	(INTEGER, r"\d+"),
	(STRING, r"\"(.*?)\""),
	(IDENTIFIER, r"[a-z_][a-z_0-9]*", re.IGNORECASE),
))

class Parser:

	def __init__(self, raw):
		self.raw = string.strip(string.expandtabs(raw))
		self.tok = None

	def parse(self):
		self.iter = scanner.scan(self.raw)
		self.iter = Lookahead(self.iter)
		self.next()
		while self.tok is not None:
			tok = self.tok
			yield Token(tok[0], tok[1], tok[2][0], tok[2][1], tok[3][0], tok[3][1], tok[4])
			self.next()

	def next(self, jump = 1):
		for _ in xrange(jump):
			self.tok = self.iter.next()
