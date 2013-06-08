import re
from collections import namedtuple

NamedPattern = namedtuple("NamedPattern", ("name", "pattern", "flags"))
Token = namedtuple("Token", ["type", "value", "srow", "scol", "erow", "ecol", "line"])

def newScanner(patterns):
    return Scanner(patterns)

JUNK_PATTERN_ID = "dzTJVa9Tp99mpkHAS49u"

class Scanner:
    def __init__(self, patterns):
        patterns = [NamedPattern(x[0], x[1], x[2] if len(x) > 2 else 0) for x in patterns]
        self.patterns = []
        for named_pattern in patterns:
            self.patterns.append(NamedPattern(named_pattern.name, re.compile(named_pattern.pattern, named_pattern.flags), named_pattern.flags))

    def scan(self, input_):
        return Iterator(self.patterns, input_)

class Iterator:
    def __init__(self, patterns, input_):
        self.patterns = patterns
        self.input = input_
        self.eofPos = len(input_)
        self.lines = input_.split("\n")
        self.pos = 0
        self.skipLine = False
        self.srow = 0
        self.scol = 0
        self.erow = 0
        self.ecol = 0
        self.line = None
        self.nle = re.compile("\n", re.MULTILINE)

    def next(self):
        tok = None
        restart_patterns = True
        while restart_patterns:
            restart_patterns = False
            for pattern in self.patterns:
                match = pattern.pattern.match(self.input, self.pos)
                if match:
                    self._updatePos(match)
                    if pattern.name == JUNK_PATTERN_ID:
                        restart_patterns = True
                        break
                    if pattern.pattern.groups < 2:
                        toktext = match.group(pattern.pattern.groups)
                    else:
                        toktext = match.groups()
                    tok = Token(pattern.name, toktext, self.srow, self.scol, self.erow, self.ecol, self.line)
                    break
        if tok is None:
            if self.pos < self.eofPos:
                raise SyntaxError("Unknown expression", (None, self.srow, self.scol, self.line))
            else:
                raise StopIteration()
        return tok

    def _updatePos(self, match):
        startPos = match.start()
        endPos = match.end()
        newLines = [_ for _ in self.nle.finditer(self.input, 0, startPos)]
        lineStart = 0
        if newLines:
            self.srow = len(newLines)
            lineStart = newLines[-1].end()
        self.line = self.lines[self.srow]
        self.scol = startPos - lineStart

        newLines = [_ for _ in self.nle.finditer(self.input, 0, endPos)]
        if newLines:
            self.erow = len(newLines)
            lineStart = newLines[-1].end()
        self.ecol = endPos - lineStart
        self.pos = endPos

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

    def lookahead(self, n=0):
        while n >= len(self.buffer):
            try:
                self.buffer.append(self.iter.next())
            except StopIteration:
                return None
        return self.buffer[n]
