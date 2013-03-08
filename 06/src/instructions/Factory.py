import A, C

def new(line):
    line = line.strip()
    if A.accept(line):
        return A.new(line)
    elif C.accept(line):
        return C.new(line)
    else:
        raise SyntaxError("Unknown instruction", (None, -1, 0, line))
