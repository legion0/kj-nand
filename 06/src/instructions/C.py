import re

DEST = (None, "M", "D", "MD", "A", "AM", "AD", "AMD")
COMP = {
    "0":    "0101010",
    "1":    "0111111",
    "-1":   "0111010",
    "D":    "0001100",
    "A":    "0110000",
    "M":    "1110000",
    "!D":   "0001101",
    "!A":   "0110001",
    "!M":   "1110001",
    "-D":   "0001111",
    "-A":   "0110011",
    "-M":   "1110011",
    "D+1":  "0011111",
    "A+1":  "0110111",
    "M+1":  "1110111",
    "D-1":  "0001110",
    "A-1":  "0110010",
    "M-1":  "1110010",
    "D+A":  "0000010",
    "D+M":  "1000010",
    "D-A":  "0010011",
    "D-M":  "1010011",
    "A-D":  "0000111",
    "M-D":  "1000111",
    "D&A":  "0000000",
    "D&M":  "1000000",
    "D|A":  "0010101",
    "D|M":  "1010101",
}
JUMP = (None, "JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP")

def joinForRE(iterable, joiner):
    strings = []
    for e in iterable:
        if e is not None:
            strings.append(re.escape(e))
    return joiner.join(strings)

RE_C_COMMAND = r"^(?:(?P<dest>" + joinForRE(DEST, "|") + r")=)?(?P<comp>" + joinForRE(COMP, "|") + r")(?:;(?P<jump>" + joinForRE(JUMP, "|") + r"))?$"

class CCommand:
    def __init__(self, dest, comp, jump):
        self.dest = dest
        self.comp = comp
        self.jump = jump
    def __str__(self):
        return "CCommand: %s=%s;%s" % (self.dest, self.comp, self.jump)
    def opcode(self):
        opcode = "111"
        opcode += COMP[self.comp]
        opcode += bin(DEST.index(self.dest))[2:].zfill(3)
        opcode += bin(JUMP.index(self.jump))[2:].zfill(3)
        return opcode

def accept(line):
    m = re.match(RE_C_COMMAND, line)
    if m:
        return m.group("dest") or m.group("jump")
    return False

def new(line):
    line = line.strip()
    if not accept(line):
        raise SyntaxError("Not a C Command", (None, -1, 0, line))
    m = re.match(RE_C_COMMAND, line)
    try:
        dest = m.group("dest")
        comp = m.group("comp")
        jump = m.group("jump")
        return CCommand(dest, comp, jump)
    except ValueError:
        raise SyntaxError("Invalid C Command", (None, -1, 0, line))
