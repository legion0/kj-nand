import re

RE_LABEL = r"[A-Za-z0-9_:.]+"

def safeLabel(label):
    return re.sub("[^A-Za-z0-9:_.]+", " ", label).replace(" ", "")