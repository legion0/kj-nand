import re

RE_A_COMMAND = r"^@(?P<value>\d+)$"

class ACommand:
    def __init__(self, val):
        if val > 2**15-1:
            raise ValueError("%d is too large." % val)
        self.val = val
    def __str__(self):
        return "ACommand: %d" % self.val
    def opcode(self):
        return bin(self.val)[2:].zfill(16)

def accept(line):
    return True if re.match(RE_A_COMMAND, line) else False

def new(line):
    line = line.strip()
    if not accept(line):
        raise SyntaxError("Not an A Command", (None, -1, 0, line))
    m = re.match(RE_A_COMMAND, line)
    value = m.group("value")
    try:
        val = int(value)
    except ValueError:
        raise SyntaxError("Invalid A Command", (None, -1, 0, line))
    try:
        return ACommand(val)
    except ValueError:
        raise SyntaxError("Value for A Command is Invalid.", (None, -1, 0, value))
