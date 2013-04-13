import re

_PUSH_ASM_CONST = """@__base__
D=A
@SP
A=M
M=D
@SP
M=M+1
"""

_PUSH_ASM_FIX = """@__base__
D=M
@SP
A=M
M=D
@SP
M=M+1
"""

_PUSH_ASM_REF = """@__base__
A=M
D=A
@__offset__
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
"""

def _cmd_push_constant(offset):
    return _PUSH_ASM_CONST.replace("__base__", str(offset))

def _cmd_push_temp(offset):
    return _PUSH_ASM_FIX.replace("__base__", "R%s" % (5+offset))

def _cmd_push_pointer(offset):
    return _PUSH_ASM_FIX.replace("__base__", "R%s" % (3+offset))

def _cmd_push_this(offset):
    return _PUSH_ASM_REF.replace("__base__", "THIS").replace("__offset__", str(offset))

def _cmd_push_that(offset):
    return _PUSH_ASM_REF.replace("__base__", "THAT").replace("__offset__", str(offset))

def _cmd_push_local(offset):
    return _PUSH_ASM_REF.replace("__base__", "LCL").replace("__offset__", str(offset))

def _cmd_push_argument(offset):
    return _PUSH_ASM_REF.replace("__base__", "ARG").replace("__offset__", str(offset))

def _cmd_push_static(offset):
    return _PUSH_ASM_FIX.replace("__base__", "__file__.%s" % offset)

_SEGMENTS = {
    "argument": _cmd_push_argument,
    "local": _cmd_push_local,
    "static": _cmd_push_static,
    "constant": _cmd_push_constant,
    "this": _cmd_push_this,
    "that": _cmd_push_that,
    "pointer": _cmd_push_pointer,
    "temp": _cmd_push_temp,
}

def joinForRE(iterable, joiner):
    strings = []
    for e in iterable:
        if e is not None:
            strings.append(re.escape(e))
    return joiner.join(strings)

_RE_ACCEPT = r"^push (?P<segment>%s) (?P<offset>\d+)$" % joinForRE(_SEGMENTS, "|")
class PushCommand:
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
commands.register(PushCommand)