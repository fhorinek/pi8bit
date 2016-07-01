start:
	set M2	1
	set	M1	0
	set B 2
loop:
	move M1 A
	inc M1
	move M1 A
	store A
	xor C
	jez end
	jmp loop
end:
	halt
