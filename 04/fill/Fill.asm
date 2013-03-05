// This file is part of the materials accompanying the book 
// "The Elements of Computing Systems" by Nisan and Schocken, 
// MIT Press. Book site: www.idc.ac.il/tecs
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

@KBD
D = A
@pixelSup
M = D

@SCREEN
D = A
@pixel
M = D

(CLEAR_SCREEN)
	@1
	D = A
	@pixel
	M = M - D
(CLEAR_SCREEN_LOOP)
	@KBD
	D = M
	@BLACK_SCREEN
	D;JGT
	
	@pixel
	D = M
	@1
	D = D + A
	@SCREEN
	D = D - A
	@CLEAR_SCREEN_LOOP
	D;JEQ
	
	@pixel
	A = M
	M = 0
	@1
	D = A
	@pixel
	M = M - D
	@CLEAR_SCREEN_LOOP
	0;JMP

(BLACK_SCREEN)
	@1
	D = A
	@pixel
	M = M + D
(BLACK_SCREEN_LOOP)
	@KBD
	D = M
	@CLEAR_SCREEN
	D;JEQ
	
	@pixelSup
	D = M
	@pixel
	D = D - M
	@BLACK_SCREEN_LOOP
	D;JEQ
	
	@pixel
	A = M
	M = -1
	@1
	D = A
	@pixel
	M = M + D
	@BLACK_SCREEN_LOOP
	0;JMP

(EXIT)
	@EXIT
	0;JMP