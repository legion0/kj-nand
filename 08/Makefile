EX=8
SOURCES = VMtranslator.py commands/*
TARGETS = VMtranslator

all: $(TARGETS)

VMtranslator: VMtranslator.py
	cp -f $< $@
	chmod +x $@

clean:
	rm -f $(TARGETS)

tar:
	tar -cvf project$(EX).tar $(SOURCES) Makefile README

