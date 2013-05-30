EX=10
SOURCES = JackAnalyzer.py compilation.py tokenizor.py
TARGETS = JackAnalyzer

all: $(TARGETS)

JackAnalyzer: JackAnalyzer.py compilation.py tokenizor.py
	cp -f $< $@
	chmod +x $@

clean:
	rm -f $(TARGETS)

tar:
	tar -cvf project$(EX).tar $(SOURCES) Makefile README
