const loops	10
start:
	set M2	1
	set	M1	0
	set B loops
loop:
	move M1 A
	inc M1
	move M1 A
	store A
	xor C
	jnz loop
end:
	halt
