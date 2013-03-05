@14
D = M
@start
M = D

@start
D = M
@next
M = D

@15
D = M
@length
M = D

@start
D = M
@length
D = D + M
@end
M = D

(LOOP0)
	// next = next + 1
	@next
	M = M + 1
	
	// Sort end ?
	@end
	D = M
	@next
	D = D - M
	@EXIT
	D;JEQ
	
	// toChange = bubbling item
	@next
	D = M
	@toChange
	M = D
	
	(SORT)
		// toChange == 0 ?
		@toChange
		D = M
		@start
		D = D - M
		@LOOP0
		D;JEQ
		
		// B > A
		@toChange
		A = M
		D = M
		A = A - 1
		D = D - M
		@LOOP0
		D;JLE
		
		// save B to temp
		@toChange
		A = M
		D = M
		@temp
		M = D
		
		// B = A
		@toChange
		A = M
		A = A - 1
		D = M
		@toChange
		A = M
		M = D
		
		// A = temp
		@temp
		D = M
		@toChange
		A = M
		A = A - 1
		M = D
		
		@toChange
		M = M - 1
		@SORT
		0;JMP
(EXIT)
	@EXIT
	0;JMP