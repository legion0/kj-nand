
TARGETS = Assembler

all: $(TARGETS)

Assembler: Assembler.py
	cp -f Assembler.py Assembler
	chmod +x Assembler

clean:
	rm -f Assembler

tar:
	tar -cvf project6.tar Makefile Assembler.py instructions/*