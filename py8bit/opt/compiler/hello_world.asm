var val 1
var ans 0

clear A
load B val
loop:
inc C
move C A
xor C
jnz loop
store A ans

halt

