import re

from commands.flow import safeLabel, RE_LABEL
from commands import functions

_RE_ACCEPT = r"^label (?P<label>%s)$" % RE_LABEL
class LabelCommand:
    def __init__(self, arg, fileName):
        self.fileName = fileName
        m = re.match(_RE_ACCEPT, arg)
        self.label = m.group("label")
    def assembly(self):
        return "(%s:%s)\n" % (functions.scope, self.label)
    @staticmethod
    def accept(arg, fileName):
        return re.match(_RE_ACCEPT, arg) is not None
import commands
commands.register(LabelCommand)
