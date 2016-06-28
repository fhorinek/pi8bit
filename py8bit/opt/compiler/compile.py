#!/usr/bin/python

import sys

global line
global line_n
global labels
global labels_adr
global address
global variabiles
global variabiles_adr

class CompileError(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return "\n\nline %u:\n\t%s\n%s" % (line_n, line, self.value)

def parse_int(text):
    if text[:2] == "0x":
        return int(text[2:], 16)
    
    if text[:2] == "0b":
        return int(text[2:], 2)
    else:
        return int(text)
    
   
def cmd_move(params):
    map_8 = {
    'a' : 0b000,
    'b' : 0b001,
    'c' : 0b010,
    'd' : 0b011,
    'x' : 0b100,
    'y' : 0b101,
    'm1': 0b110,
    'm2': 0b111}
    
    map_16_src = {
    'pc' : 0b000,
    'inc' : 0b001,
    'j' : 0b010,
    'm' : 0b011,
    'xy' : 0b100,
    'ffff' : 0b101,
    '0000': 0b110}
    
    map_16_dst = {
    'pc' : 0b0,
    'xy': 0b1}
    
    if len(params) <> 2:
        raise CompileError("Exactly 2 parameters required!")
    
    if params[0] in map_8 and params[1] in map_8:
        a = 0b00000000 | map_8[params[0]] << 3 | map_8[params[1]]
        return [a]
    
    if params[0] in map_16_src and params[1] in map_16_dst:
        a = 0b10111000 | map_16_src[params[0]] | map_16_dst[params[1]]
        return [a]
    
    raise CompileError("Invalid source or destination register")
   
    
def cmd_load(params):
    map_8 = {
    'a' : 0b000,
    'b' : 0b001,
    'c' : 0b010,
    'd' : 0b011,
    'x' : 0b100,
    'y' : 0b101,
    'j1': 0b110,
    'j2': 0b111}
    
    if len(params) < 1:
        raise CompileError("At least 1 parameter required!")
    
    a = 0b10111000         
    b = 0b10101000 | map_8[params[0]]
    
    if params[0] not in map_8:
        raise CompileError("Invalid destination register")    
    
    if len(params) == 1:
        return [b]
    
    if params[1] in variabiles:
        variabiles_adr[address + 1] = params[1]
        return [a, 0, 0, b]
    
    adr = parse_int(params[1])
    lo = (adr & 0x00FF) >> 0
    hi = (adr & 0xFF00) >> 8
    return [a, lo, hi, b]

    
def cmd_store(params):
    map_8 = {
    'a' : 0b000,
    'b' : 0b001,
    'c' : 0b010,
    'd' : 0b011,
    'x' : 0b100,
    'y' : 0b101,
    'ff': 0b110,
    '00': 0b111}
    
    if len(params) < 1:
        raise CompileError("At least 1 parameter required!")
    
    if params[0] not in map_8:
        raise CompileError("Invalid source register")
        
    a = 0b10111000         
    b = 0b10110000 | map_8[params[0]]
        
    if len(params) == 1:
        return [b]
   
    if params[1] in variabiles:
        variabiles_adr[address + 1] = params[1]
        return [a, 0, 0, b]   
   
    adr = parse_int(params[1])
    lo = (adr & 0x00FF) >> 0
    hi = (adr & 0xFF00) >> 8
    return [a, lo, hi, b]
    
def cmd_set(params):
    map_8 = {
    'a' : 0b000,
    'b' : 0b001,
    'c' : 0b010,
    'd' : 0b011,
    'x' : 0b100,
    'y' : 0b101,
    'm1': 0b110,
    'm2': 0b111}
    
    map_16 = {
    'm' : 0b00,
    'xy': 0b01,
    'j' : 0b10,
    'ab': 0b11}
    
    if len(params) <> 2:
        raise CompileError("Exactly 2 parameters required!")
    
    if params[0] in map_8:
        a = 0b10100000 | map_8[params[0]]
        val = parse_int(params[1])
        return [a, val]
    
    if params[0] in map_16:
        a = 0b10111000 | map_16[params[0]]
        val = parse_int(params[1])
        lo = (val & 0x00FF) >> 0
        hi = (val & 0xFF00) >> 8
        return [a, lo, hi]
    
    raise CompileError("Invalid destination register")

alu_op = {
    "add" : 0b000,
    "inc" : 0b001,
    "and" : 0b010,
    "or"  : 0b011,
    "xor" : 0b100,
    "not" : 0b101,
    "shl" : 0b110,
    "nop" : 0b111,
}

def cmd_alu(op, params):
    map_8 = {
    'j1' : 0b000,
    'j2' : 0b001,
    'c' : 0b010,
    'd' : 0b011,
    'x' : 0b100,
    'y' : 0b101,
    'm1': 0b110,
    'm2': 0b111}    

    
    if op <> "nop" and len(params) <> 1: 
        raise CompileError("Exactly 1 parameter required!")
    
    if op == "nop" and len(params) <> 0:
        raise CompileError("No parameter required!")

    if op == "nop" and len(params) == 0:
        params.append("j1")
    
    return [0b01000000 | (alu_op[op] << 3) | map_8[params[0]]]  

jump_op = {
    "jmp" : 0b0000,
    "jze" : 0b0100,
    "jnz" : 0b1100,
    "jov" : 0b0010,
    "jno" : 0b1010,
    "jsi" : 0b0001,
    "jns" : 0b1001,
}

def cmd_jump(op, params):
    a = 0b10111010         
    b = 0b10010000 | jump_op[op]

    if len(params) == 0: 
        return [b]
    
    labels_adr[address + 1] = params[0]
    
    return [a, 0, 0, b]

def cmd_call(params):
    if len(params) <> 1: 
        raise CompileError("Exactly 1 parameter required!")

    labels_adr[address + 1] = params[0]

    a = 0b10111010         
    b = 0b10111100
    return [a, 0, 0, b]

filename = "hello_world.asm"#sys.argv[1]
output = "out.a"

f = open(filename, "r")
b = open(output, "wb")


line_n = 0
address = 0
labels = {}
labels_adr = {}
variabiles = {}
variabiles_loc = {}
variabiles_adr = {}

program = []

for line in f.readlines():
    print line.replace("\n", "")
    data = line.lower().split()
    if len(data) == 0:
        continue
    
    if data[0][0] == "#":
        continue
    
    if data[0][0] == ":":
        labels[data[0][1:]] = address
        continue    

    cmd = data[0]
    params = data[1:]

    if cmd == "var":
        if len(params) <> 2:
            raise CompileError("Exactly 2 parameters required!")
        variabiles[params[0]] = parse_int(params[1])
        continue
    
    inst = ""
    if cmd == "set":
        inst = cmd_set(params)

    if cmd == "move":
        inst = cmd_move(params)

    if cmd == "load":
        inst = cmd_load(params)

    if cmd == "store":
        inst = cmd_store(params)
    
    if cmd in alu_op:
        inst = cmd_alu(cmd, params)

    if cmd in jump_op:
        inst = cmd_jump(cmd, params)
    
    if cmd == "call":
        inst = cmd_call(params)    
    
    if cmd == "ret":
        inst = [0b10111101]
        
    if cmd == "halt":
        inst = [0b10111110]        
    
    if len(inst) == 0:
        raise CompileError("Unknown command!")
    
    print ">",
    for i in inst:
        print "%02X" % i,
    print
    
    program += inst
    address += len(inst)
    line_n += 1
    
print "\nReplacing labels with address"    
    
for loc in labels_adr:
    if labels_adr[loc] not in labels:
        raise Exception("Unknown label '%s'!" % labels_adr[loc])
    
    adr = labels[labels_adr[loc]]
    lo = (adr & 0x00FF) >> 0
    hi = (adr & 0xFF00) >> 8
    program[loc + 0] = lo
    program[loc + 1] = hi
    
    print "\t0x%04X\t%s\t0x%02X" % (loc, labels_adr[loc], adr)
    
print "\nWriting variabiles section"    
    
for var_name in variabiles:
    variabiles_loc[var_name] = len(program)
    program.append(variabiles[var_name])
    print "\t0x%04X\t%s\t0x%02X" % (variabiles_loc[var_name], var_name, variabiles[var_name])
    
for loc in variabiles_adr:
    adr = variabiles_loc[variabiles_adr[loc]]
    lo = (adr & 0x00FF) >> 0
    hi = (adr & 0xFF00) >> 8
    program[loc + 0] = lo
    program[loc + 1] = hi   

b.write("".join(map(chr, program)))    

f.close()
b.close()
    
