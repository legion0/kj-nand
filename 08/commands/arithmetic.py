import re

_a_cmd_id = -1
def _nextCid():
    global _a_cmd_id
    _a_cmd_id += 1
    return _a_cmd_id

_cmd_a_add = """@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M+D
@SP
M=M+1
"""

_cmd_a_sub = """@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M-D
@SP
M=M+1
"""

_cmd_a_and = """@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M&D
@SP
M=M+1
"""

_cmd_a_or = """@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M|D
@SP
M=M+1
"""

def _cmd_a_eq():
    cid = _nextCid()
    return """@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@L_EQ___id___EQ
D; JEQ
@0
D=A
@L_EQ___id___END
0;JMP
(L_EQ___id___EQ)
@0
A=A-1
D=A
@L_EQ___id___END
0;JMP
(L_EQ___id___END)
@SP
A=M
M=D
@SP
M=M+1
""".replace("__id__", str(cid))

def _cmd_a_gt():
    cid = _nextCid()
    return """@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@L_EQ___id___EQ
D; JGT
@0
D=A
@L_EQ___id___END
0;JMP
(L_EQ___id___EQ)
@0
A=A-1
D=A
@L_EQ___id___END
0;JMP
(L_EQ___id___END)
@SP
A=M
M=D
@SP
M=M+1
""".replace("__id__", str(cid))

def _cmd_a_lt():
    cid = _nextCid()
    return """@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D
@L_EQ___id___EQ
D; JLT
@0
D=A
@L_EQ___id___END
0;JMP
(L_EQ___id___EQ)
@0
A=A-1
D=A
@L_EQ___id___END
0;JMP
(L_EQ___id___END)
@SP
A=M
M=D
@SP
M=M+1
""".replace("__id__", str(cid))

_cmd_a_neg = """@0
D=A
@SP
M=M-1
A=M
M=D-M
@SP
M=M+1
"""

_cmd_a_not = """@SP
M=M-1
A=M
M=!M
@SP
M=M+1
"""

_A_COMMANDS = {
    "add": _cmd_a_add,
    "sub": _cmd_a_sub,
    "neg": _cmd_a_neg,
    "eq": _cmd_a_eq,
    "gt": _cmd_a_gt,
    "lt": _cmd_a_lt,
    "and": _cmd_a_and,
    "or": _cmd_a_or,
    "not": _cmd_a_not,
}

def joinForRE(iterable, joiner):
    strings = []
    for e in iterable:
        if e is not None:
            strings.append(re.escape(e))
    return joiner.join(strings)

_RE_ACCEPT = r"^(?P<command>%s)$" % joinForRE(_A_COMMANDS, "|")
class ArithmeticCommand:
    def __init__(self, arg, fileName):
        self.cmd = re.match(_RE_ACCEPT, arg).group("command")
    def assembly(self):
        val = _A_COMMANDS[self.cmd]
        if callable(val):
            val = val()
        return val
    @staticmethod
    def accept(arg, fileName):
        return re.match(_RE_ACCEPT, arg) is not None
import commands
commands.register(ArithmeticCommand)
