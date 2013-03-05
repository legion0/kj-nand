// This file is part of the materials accompanying the book 
// "The Elements of Computing Systems" by Nisan and Schocken, 
// MIT Press. Book site: www.idc.ac.il/tecs
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[3], respectively.)

@sum
M = 0
@0
D = M
@counter
M = D
@1
D = M
@mul
M = D

(LOOP0)
	@counter
	D = M
	@LOOP0_END
	D;JEQ
	@1
	D = D - A
	@counter
	M = D
	@mul
	D = M
	@sum
	M = M + D
	@LOOP0
	0;JMP
(LOOP0_END)
	@sum
	D = M
	@2
	M = D
	@EXIT
	0;JMP

(EXIT)
	@EXIT
	0;JMP