import re

scope = ""

RE_NAME = r"[A-Za-z0-9_.]+"

def safeName(name):
    return re.sub("[^A-Za-z0-9_.]+", " ", name).replace(" ", "")