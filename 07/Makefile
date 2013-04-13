SOURCES = translator.py
TARGETS = translator project7.tar

all: $(TARGETS)

translator: translator.py
	cp -f $< $@
	chmod +x $@

clean:
	rm -f $(TARGETS)

tar: project7.tar
project7.tar: $(SOURCES) Makefile README
	tar -cvf $@ $^ 
