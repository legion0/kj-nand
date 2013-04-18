EX=6

SOURCES = Assembler.py instructions/*
TARGETS = Assembler

all: $(TARGETS)

Assembler: Assembler.py
	cp -f $< $@
	chmod +x $@

clean:
	rm -f $(TARGETS)

tar:
	tar -cvf project$(EX).tar $(SOURCES) Makefile README

