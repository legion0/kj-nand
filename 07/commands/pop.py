import re

_POP_ASM_FIX = """@SP
M=M-1
A=M
D=M
@__base__
M=D
"""

_POP_ASM_REF = """@__base__
A=M
D=A
@__offset__
D=D+A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
"""

def _cmd_pop_constant(offset):
    return _POP_ASM_FIX.replace("__base__", str(offset))

def _cmd_pop_temp(offset):
    return _POP_ASM_FIX.replace("__base__", "R%s" % (5 + offset))

def _cmd_pop_pointer(offset):
    return _POP_ASM_FIX.replace("__base__", "R%s" % (3 + offset))

def _cmd_pop_this(offset):
    return _POP_ASM_REF.replace("__base__", "THIS").replace("__offset__", str(offset))

def _cmd_pop_that(offset):
    return _POP_ASM_REF.replace("__base__", "THAT").replace("__offset__", str(offset))

def _cmd_pop_local(offset):
    return _POP_ASM_REF.replace("__base__", "LCL").replace("__offset__", str(offset))

def _cmd_pop_argument(offset):
    return _POP_ASM_REF.replace("__base__", "ARG").replace("__offset__", str(offset))

def _cmd_pop_static(offset):
    return _POP_ASM_FIX.replace("__base__", "__file__.%s" % offset)

_SEGMENTS = {
    "argument": _cmd_pop_argument,
    "local": _cmd_pop_local,
    "static": _cmd_pop_static,
    "constant": _cmd_pop_constant,
    "this": _cmd_pop_this,
    "that": _cmd_pop_that,
    "pointer": _cmd_pop_pointer,
    "temp": _cmd_pop_temp,
}

def joinForRE(iterable, joiner):
    strings = []
    for e in iterable:
        if e is not None:
            strings.append(re.escape(e))
    return joiner.join(strings)

_RE_ACCEPT = r"^pop (?P<segment>%s) (?P<offset>\d+)$" % joinForRE(_SEGMENTS, "|")
class PopCommand:
    def __init__(self, arg, fileName):
        self.fileName = fileName
        m = re.match(_RE_ACCEPT, arg)
        segment = m.group("segment")
        self.cmd = _SEGMENTS[segment]
        self.offset = int(m.group("offset"))
    def assembly(self):
        return self.cmd(self.offset).replace("__file__", self.fileName)
    @staticmethod
    def accept(arg, fileName):
        return re.match(_RE_ACCEPT, arg) is not None
import commands
commands.register(PopCommand)
