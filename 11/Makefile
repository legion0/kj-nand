EX=11
SOURCES = compilation.py JackCompiler.py scanner.py symbol_table.py tokenizor.py vm_writer.py
TARGETS = JackCompiler

all: $(TARGETS)

JackCompiler: $(SOURCES)
	cp -f $@.py $@
	chmod +x $@

clean:
	rm -f $(TARGETS) *.pyc

tar:
	tar -cvf project$(EX).tar $(SOURCES) Makefile README
