import re
import random, string

from commands.functions import safeName, RE_NAME
from commands import functions

_PUSH_STR = """@__value__
D=A
@SP
A=M
M=D
@SP
M=M+1
"""

_PUSH_STR_REF = """@__value__
D=M
@SP
A=M
M=D
@SP
M=M+1
"""

_ARG_LCL_UPDATE_STR = """@SP
D=M
@__value__
D=D-A
@5
D=D-A
@ARG
M=D
@SP
D=M
@LCL
M=D
"""

_JMP_STR = """@__value__
0; JMP
"""

_randPower = 32

def _make_rand_id():
    _make_rand_id.salt += 1
    randStr = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(_randPower))
    return "%s_%s" % (str(_make_rand_id.salt), randStr)
_make_rand_id.salt = 0

_RE_ACCEPT = r"^call (?P<name>%s) (?P<args>\d+)$" % RE_NAME
class FunctionCallCommand:
    def __init__(self, arg, fileName):
        self.fileName = fileName
        m = re.match(_RE_ACCEPT, arg)
        self.fName = m.group("name")
        self.argc = m.group("args")
    def assembly(self):
        self.returnLabel = "LABEL_RET_%s_%s" % (functions.scope, _make_rand_id())
        asmStr = self.push_stuff_asm()
        asmStr += _ARG_LCL_UPDATE_STR.replace("__value__", str(self.argc))
        asmStr += _JMP_STR.replace("__value__", self.fName)
        asmStr += "(%s)" % self.returnLabel
        return asmStr
    def push_stuff_asm(self):
        asmStr = _PUSH_STR.replace("__value__", self.returnLabel)
        asmStr += _PUSH_STR_REF.replace("__value__", "LCL")
        asmStr += _PUSH_STR_REF.replace("__value__", "ARG")
        asmStr += _PUSH_STR_REF.replace("__value__", "THIS")
        asmStr += _PUSH_STR_REF.replace("__value__", "THAT")
        return asmStr
    @staticmethod
    def accept(arg, fileName):
        return re.match(_RE_ACCEPT, arg) is not None
import commands
commands.register(FunctionCallCommand)
