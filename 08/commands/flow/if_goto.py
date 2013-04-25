import re

from commands.flow import safeLabel, RE_LABEL
from commands import functions

JMP_STR = """@SP
M=M-1
A=M
D=M
@__label__
D; JNE
"""

_RE_ACCEPT = r"^if-goto (?P<label>%s)$" % RE_LABEL
class IfGotoCommand:
    def __init__(self, arg, fileName):
        self.fileName = fileName
        m = re.match(_RE_ACCEPT, arg)
        self.label = m.group("label")
    def assembly(self):
        newLabel = "%s:%s" % (functions.scope, self.label)
        return JMP_STR.replace("__label__", newLabel)
    @staticmethod
    def accept(arg, fileName):
        return re.match(_RE_ACCEPT, arg) is not None
import commands
commands.register(IfGotoCommand)
