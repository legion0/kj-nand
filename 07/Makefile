EX=7
SOURCES = VMtranslator.py commands/*.py tools/*.py
TARGETS = VMtranslator

all: $(TARGETS)

VMtranslator: VMtranslator.py
	cp -f $< $@
	chmod +x $@

clean:
	rm -f $(TARGETS)

tar:
	tar -cvf project$(EX).tar $(SOURCES) Makefile README

