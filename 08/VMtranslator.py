#! /usr/bin/env python
_DEBUG = False

import commands as Factory
import sys, os
import re
import glob

SCRIPT_DIR = os.path.dirname(__file__)

def importCommands(path):
    modules = glob.glob(os.path.join(SCRIPT_DIR, path, "*.py"))
    modules = [os.path.basename(x)[:-3] for x in modules]
    modules = [x for x in modules if x != "__init__"]
    __import__(path.replace(os.sep, "."), globals(), locals(), modules)

importCommands("commands")
for name in os.listdir(os.path.join(SCRIPT_DIR, "commands")):
    if os.path.isfile(os.path.join(SCRIPT_DIR, "commands", name, "__init__.py")):
        importCommands(os.path.join("commands", name))

USAGE_MSG = """USAGE: %s <.asm file>""" % os.path.basename(__file__)

_PUSH_STR = """@0
D=A
@SP
A=M
M=D
@SP
M=M+1
"""

BOOTSTRAP_CODE = """@256
D=A
@SP
M=D
""" + (_PUSH_STR * 5) + """@Sys.init
0; JMP
"""

def main(argv):
    if len(argv) < 1:
        print >> sys.stderr, USAGE_MSG
        exit(-1)
    filePath = argv[0]
    try:
        fileList = []
        if os.path.isdir(filePath):
            dirPath = filePath
            if dirPath.endswith(os.sep):
                dirPath = dirPath[:-len(os.sep)]
            dirName = os.path.basename(dirPath)
            outFilePath = os.path.join(dirPath, "%s.asm" % dirName)
            for fileName in os.listdir(dirPath):
                baseName, fileExt = os.path.splitext(fileName)
                if fileExt.lower() != ".vm":
                    continue
                fileList.append(fileName)
        else:
            dirPath, fileName = os.path.split(filePath)
            baseName, _ = os.path.splitext(fileName)
            outFilePath = os.path.join(dirPath, "%s.asm" % baseName)
            fileList.append(fileName)
        commands = []
        for fileName in fileList:
            baseName, _ = os.path.splitext(fileName)
            filePath = os.path.join(dirPath, fileName)
            with open(filePath, "r") as f:
                lines = f.readlines()
            lines = cleanLines(lines)
            commands.extend(compile_(lines, baseName))
            assembly = toAssembly(commands)
            assembly = '\n'.join(assembly)
            assembly = BOOTSTRAP_CODE + assembly
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
#     main([r"C:\Users\Yotam\Documents\Studies\NAND\projects\08\ProgramFlow\BasicLoop\BasicLoop.vm"])
#     main([r"C:\Users\Yotam\Documents\Studies\NAND\projects\08\ProgramFlow\FibonacciSeries\FibonacciSeries.vm"])
#     main([r"C:\Users\Yotam\Documents\Studies\NAND\projects\08\FunctionCalls\SimpleFunction\SimpleFunction.vm"])
#     main([r"C:\Users\Yotam\Documents\Studies\NAND\projects\08\FunctionCalls\FibonacciElement"])
#     main([r"C:\Users\Yotam\Documents\Studies\NAND\projects\08\FunctionCalls\StaticsTest"])
