import re
import random, string

from commands.functions import safeName, RE_NAME
from commands import functions

_RET_STR = """@LCL // FRAME=LCL
D=M
@R13 // FRAME
M=D
// RET=*(FRAME-5)
@R13
D=M
@5
A=D-A
D=M
@R14 // RET
M=D
// *ARG = pop()
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
// SP=ARG+1
@ARG
D=M
D=D+1
@SP
M=D
// THAT=*(FRAME-1)
@R13
D=M
@1
D=D-A
A=D
D=M
@THAT
M=D
// THIS=*(FRAME-2)
@R13
D=M
@2
D=D-A
A=D
D=M
@THIS
M=D
// ARG=*(FRAME-3)
@R13
D=M
@3
D=D-A
A=D
D=M
@ARG
M=D
// LCL=*(FRAME-4)
@R13
D=M
@4
D=D-A
A=D
D=M
@LCL
M=D
// goto RET
@R14
A=M
0; JMP
"""

_RE_ACCEPT = r"^return$"
class FunctionReturnCommand:
    def __init__(self, arg, fileName):
        self.fileName = fileName
        m = re.match(_RE_ACCEPT, arg)
    def assembly(self):
        return _RET_STR
    @staticmethod
    def accept(arg, fileName):
        return re.match(_RE_ACCEPT, arg) is not None
import commands
commands.register(FunctionReturnCommand)
