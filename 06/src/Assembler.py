#! /usr/bin/env python
_DEBUG = False

import sys, os, re
from instructions import Factory

MEM_START = 16

SYMBOLS = {
   "SP": 0,
   "LCL": 1,
   "ARG": 2,
   "THIS": 3,
   "THAT": 4,
   "R0": 0,
   "R1": 1,
   "R2": 2,
   "R3": 3,
   "R4": 4,
   "R5": 5,
   "R6": 6,
   "R7": 7,
   "R8": 8,
   "R9": 9,
   "R10": 10,
   "R11": 11,
   "R12": 12,
   "R13": 13,
   "R14": 14,
   "R15": 15,
   "SCREEN": 16384,
   "KBD": 24576,
}

USAGE_MSG = """USAGE: Assembler <.asm file>"""
RE_SYMBOL = r"(?P<symbol>[a-zA-Z_.:$][a-zA-Z_.:$0-9]*)"
RE_LABEL = r"^\("+RE_SYMBOL+"\)$"
RE_SYMBOLIC_A = r"^@"+RE_SYMBOL+"$"

def main(argv):
    if len(argv) < 1:
        print >> sys.stderr, USAGE_MSG
        exit(-1)
    filePath = argv[0]
    try:
        with open(filePath, "r") as f:
            lines = f.readlines()
        
        lines = cleanLines(lines)
        lines = resolveSymbols(lines)
        assembly = toAssembly(lines)
        opcodes = toOpcodes(assembly)
        
        outFilePath = os.path.splitext(filePath)[0] + ".hack"
        with open(outFilePath, "w") as f:
            for opcode in opcodes:
                f.write(opcode + "\n")
    except SyntaxError as ex:
        ex.filename = filePath
        die(ex)
    except IOError as ex:
        die(ex)
    except Exception as ex:
        die(ex)

def cleanLines(lines):
    newLines = []
    for i in xrange(len(lines)):
        line = lines[i]
        commentStart = line.find("//")
        if commentStart != -1:
            line = line[:commentStart]
        line = re.sub("\s+", "", line).strip()
        if line == "":
            continue
        newLines.append((line, i))
    return newLines

def resolveSymbols(lines):
    labels = {}
    newLines = []
    for i in xrange(len(lines)):
        line = lines[i][0]
        m = re.match(RE_LABEL, line)
        if m:
            label = m.group('symbol')
            if label in labels:
                raise SyntaxError("label redefined", (None, lines[i][1], 0, line))
            if label in SYMBOLS:
                raise SyntaxError("symbol redefined", (None, lines[i][1], 0, line))
            currentLength = len(labels)
            labels[label] = i - currentLength
        else:
            newLines.append((line, lines[i][1]))
    lines = newLines
    
    memoryIndex = MEM_START
    memSymbols = {}
    for i in xrange(len(lines)):
        line = lines[i][0]
        m = re.match(RE_SYMBOLIC_A, line)
        if m:
            symbol = m.group("symbol")
            if symbol in SYMBOLS:
                line = line.replace(symbol, str(SYMBOLS[symbol]))
            elif symbol in labels:
                line = line.replace(symbol, str(labels[symbol]))
            else:
                if symbol not in memSymbols:
                    memSymbols[symbol] = memoryIndex
                    memoryIndex += 1
                line = line.replace(symbol, str(memSymbols[symbol]))
            lines[i] = (line, lines[i][1])
    return lines

def toAssembly(lines):
    commands = []
    for line, lineno in lines:
        try:
            cmd = Factory.new(line)
            commands.append(cmd)
        except SyntaxError as ex:
            ex.lineno = lineno
            raise ex
    return commands

def toOpcodes(assembly):
    opcodes = []
    for cmd in assembly:
        opcodes.append(cmd.opcode())
    return opcodes

def die(ex):
#    print >> sys.stderr, "ERROR: %s (%d)" % (ex.strerror, ex.errno)
    if isinstance(ex, SyntaxError):
        print >> sys.stderr, "ERROR: %s at line: %d, %s." % (ex.msg, ex.lineno, ex.text)
    elif isinstance(ex, IOError):
        print >> sys.stderr, "ERROR: %s (%d)." % (ex.strerror, ex.errno)
    else:
        if _DEBUG:
            raise ex
        else:
            print >> sys.stderr, "ERROR: UNKNOWN."
    exit(-3)
    
if __name__ == '__main__':
    main(sys.argv[1:])
