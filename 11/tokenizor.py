import re, string
from scanner import newScanner, JUNK_PATTERN_ID

SYMBOL = "SYMBOL"
KEYWORD = "KEYWORD"
IDENTIFIER = "IDENTIFIER"
INTEGER = "INTEGER"
STRING = "STRING"

def newTokenizor(source):
	return my_scanner.scan(string.expandtabs(source))

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
_RE_KEYWORD = "(?:" + "|".join([re.escape(x) for x in _KEYWORDS]) + ")(?![a-zA-Z_])"

my_scanner = newScanner((
	(JUNK_PATTERN_ID, r"//.*\n"),
	(JUNK_PATTERN_ID, r"/\*.*?\*/", re.DOTALL),
	(JUNK_PATTERN_ID, r"\n"),
	(JUNK_PATTERN_ID, r"\r"),
	(JUNK_PATTERN_ID, r" "),
	(KEYWORD, _RE_KEYWORD),
	(SYMBOL, _RE_SYM),
	(INTEGER, r"\d+"),
	(STRING, r"\"(.*?)\""),
	(IDENTIFIER, r"[a-z_][a-z_0-9]*", re.IGNORECASE),
))
