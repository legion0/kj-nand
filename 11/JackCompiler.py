#!/usr/bin/env python
import sys, os
from compilation import CompilationEngine

USAGE_MSG = "USAGE: JackCompiler <source>"

def main(argv):
	if len(argv) != 1:
		die(USAGE_MSG)
	filePath = argv[0]
	fileList = []
	if os.path.isdir(filePath):
		dirPath = filePath
		if dirPath.endswith(os.sep):
			dirPath = dirPath[:-len(os.sep)]
		for fileName in os.listdir(dirPath):
			baseName, fileExt = os.path.splitext(fileName)
			if fileExt.lower() != ".jack":
				continue
			fileList.append(fileName)
	else:
		dirPath, fileName = os.path.split(filePath)
		fileList.append(fileName)
	for fileName in fileList:
# 		print fileName
		filePath = os.path.join(dirPath, fileName)
		baseName, _ = os.path.splitext(fileName)
		with open(filePath) as f:
			source = f.read()
		outFileName = "%s.vm" % (baseName)
		outFilePath = os.path.join(dirPath, outFileName)
		with open(outFilePath, "w") as f:
			compiler = CompilationEngine(source, f)
# 			try:
			compiler.compile()
# 			except SyntaxError as ex:
# 				ex.filename = fileName
# 				die(ex)

def die(ex):
	if isinstance(ex, basestring):
		print >> sys.stderr, ex
	elif isinstance(ex, SyntaxError):
		print >> sys.stderr, formatSyntaxError(ex)
	elif isinstance(ex, IOError):
		print >> sys.stderr, "ERROR: %s (%d)." % (ex.strerror, ex.errno)
	else:
		print >> sys.stderr, "ERROR: UNKNOWN."
	exit(-1)

SYNTAX_ERROR_TEMPLATE = """File "__FILE__", line __LINENO__
__LINE__
__SPACES__^
SyntaxError: __MSG__"""

def formatSyntaxError(ex):
	return SYNTAX_ERROR_TEMPLATE.replace("__FILE__", ex.filename).replace("__LINENO__", str(ex.lineno)).replace("__LINE__", ex.text.rstrip()).replace("__SPACES__", " " * ex.offset).replace("__MSG__", ex.msg)

if __name__ == "__main__":
# 	main([r"D:\My Documents\Stud\2012-2013\NAND\workspace\10\ArrayTest"])
#  	main([r"D:\My Documents\Stud\2012-2013\NAND\workspace\10\ExpressionlessSquare"])
# 	main([r"D:\My Documents\Stud\2012-2013\NAND\workspace\10\ExpressionlessSquare\SquareGame.jack"])
  	main([r"D:\My Documents\Stud\2012-2013\NAND\workspace\11\ConvertToBin\Main.jack"])
# 	main([r"D:\My Documents\Stud\2012-2013\NAND\workspace\11\Seven"])
# 	main(sys.argv[1:])
