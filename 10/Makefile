EX=10
SOURCES = JackCompiler.py compilation.py tokenizor.py
TARGETS = JackCompiler

all: $(TARGETS)

JackCompiler: JackCompiler.py compilation.py tokenizor.py
	cp -f $< $@
	chmod +x $@

clean:
	rm -f $(TARGETS)

tar:
	tar -cvf project$(EX).tar $(SOURCES) Makefile README
