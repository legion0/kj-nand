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

_RE_ACCEPT = r"^function (?P<name>%s) (?P<args>\d+)$" % RE_NAME
class FunctionDeclareCommand:
    def __init__(self, arg, fileName):
        self.fileName = fileName
        m = re.match(_RE_ACCEPT, arg)
        self.fName = m.group("name")
        self.argc = int(m.group("args"))
    def assembly(self):
        functions.scope = safeName(self.fName)
        asmStr = "(%s)\n" % functions.scope
        asmStr += _PUSH_STR.replace("__value__", "0") * self.argc
        return asmStr
    @staticmethod
    def accept(arg, fileName):
        return re.match(_RE_ACCEPT, arg) is not None
import commands
commands.register(FunctionDeclareCommand)
