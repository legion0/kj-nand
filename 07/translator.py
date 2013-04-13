#! /usr/bin/env python
_DEBUG = False

from commands.push import PushCommand
from commands.arithmetic import ArithmeticCommand
from commands.pop import PopCommand
import commands as Factory

import sys, os, re

USAGE_MSG = """USAGE: %s <.asm file>""" % os.path.basename(__file__)

def main(argv):
    if len(argv) < 1:
        print >> sys.stderr, USAGE_MSG
        exit(-1)
    filePath = argv[0]
    baseName = os.path.splitext(os.path.basename(filePath))[0]
    outFilePath = os.path.join(os.path.split(filePath)[0], "%s.asm" % baseName)
    try:
        with open(filePath, "r") as f:
            lines = f.readlines()
        lines = cleanLines(lines)
        commands = compile_(lines, baseName)
        assembly = toAssembly(commands)
        assembly = '\n'.join(assembly)
        
#         outFilePath = os.path.splitext(filePath)[0] + ".asm"
        with open(outFilePath, "w") as f:
            f.write(assembly)
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
        line = re.sub("\s+", " ", line).strip()
        if line == "":
            continue
        newLines.append((line, i))
    return newLines

def compile_(lines, baseName):
    commands = []
    for line, lineno in lines:
        try:
            cmd = Factory.new(line, baseName)
            if cmd is None:
                raise SyntaxError("Unknown Command", (None, lineno, 0, line))
            commands.append(cmd)
        except SyntaxError as ex:
            ex.lineno = lineno
            raise ex
    return commands

def toAssembly(commands):
    assembly = []
    for cmd in commands:
        assembly.append(cmd.assembly().strip())
    return assembly

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
#     main(sys.argv[1:])
    main([r"C:\Users\Yotam\Documents\Studies\NAND\projects\07\StackArithmetic\SimpleAdd\SimpleAdd.vm"])
    main([r"C:\Users\Yotam\Documents\Studies\NAND\projects\07\StackArithmetic\StackTest\StackTest.vm"])
    main([r"C:\Users\Yotam\Documents\Studies\NAND\projects\07\MemoryAccess\BasicTest\BasicTest.vm"])
    main([r"C:\Users\Yotam\Documents\Studies\NAND\projects\07\MemoryAccess\PointerTest\PointerTest.vm"])
    main([r"C:\Users\Yotam\Documents\Studies\NAND\projects\07\MemoryAccess\StaticTest\StaticTest.vm"])
