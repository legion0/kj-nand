EX=5
COMPILER=
CFLAGS=
LINKER=
SOURCES = Memory.hdl CPU.hdl Computer.hdl JumpCalc.hdl
TARGETS = ex$(EX).tar

all: $(TARGETS)

ex$(EX).tar: $(SOURCES) README
	tar -cf $@ $^

clean:
	rm -f $(TARGETS) *.out
