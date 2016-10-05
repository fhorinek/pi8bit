#!/usr/bin/python

import sys
from collections import OrderedDict

global line
global line_n

global labels
global labels_loc
global labels_adr

global address

global variabiles
global variabiles_loc
global variabiles_adr

global constants

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
    
    val = int(text)
    
    if val < 0:
        return val + 256
    else:
        return val
    
def cmd_clear(params):
    map_8 = {
    'a' : 0b000,
    'b' : 0b001,
    'c' : 0b010,
    'd' : 0b011,
    'x' : 0b100,
    'y' : 0b101,
    'm1': 0b110,
    'm2': 0b111}
    
    if len(params) <> 1:
        raise CompileError("Exactly 1 parameter is required!")
    
    if params[0] in map_8:
        a = 0b00000000 | map_8[params[0]] << 3 | map_8[params[0]]
        return [a]
    
    raise CompileError("Invalid source or destination register")    
   
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
        a = 0b10000000 | map_16_src[params[0]] << 1 | map_16_dst[params[1]]
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
        if params[1] in constants:
            val = 0xFF & constants[params[1]]
        else:                
            val = parse_int(params[1])
            
        return [a, val]
    
    if params[0] in map_16:
        a = 0b10111000 | map_16[params[0]]
        
        if params[1] in labels:
            labels_adr[address + 1] = params[1]
            val = 0
        elif params[1] in variabiles:
            variabiles_adr[address + 1] = params[1]
            val = 0
        elif params[1] in constants:
            val = 0xFFFF & constants[params[1]]
        else:
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
    "jez" : 0b0100,
    "jnz" : 0b1100,
    "jeo" : 0b0010,
    "jno" : 0b1010,
    "jes" : 0b0001,
    "jns" : 0b1001,
}

def cmd_jump(op, params):
    a = 0b10111010         
    b = 0b10010000 | jump_op[op]

    if len(params) == 0: 
        return [b]

    if params[0] in labels: 
        labels_adr[address + 1] = params[0]
        val = 0
    elif params[0] in constants:
        val = constants[params[0]]
    else:
        val = parse_int(params[0])
        
    lo = (val & 0x00FF) >> 0
    hi = (val & 0xFF00) >> 8   
     
    return [a, lo, hi, b]

def cmd_call(params):
    a = 0b10111010         
    b = 0b10111100

    if len(params) == 0: 
        return [b]

    if params[0] in labels: 
        labels_adr[address + 1] = params[0]
        val = 0
    elif params[0] in constants:
        val = constants[params[0]]
    else:
        val = parse_int(params[0])

    lo = (val & 0x00FF) >> 0
    hi = (val & 0xFF00) >> 8   
    
    return [a, lo, hi, b]

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "hello_world.asm"
    
output = "out.a"

f = open(filename, "r")
b = open(output, "wb")


line_n = 0
address = 0
labels = []
labels_loc = {}
labels_adr = {}
variabiles = OrderedDict()
variabiles_loc = {}
variabiles_adr = {}
constants = {}


program = []

print "compiling file", filename
print "output file is", output
print

lines = f.readlines()

for line in lines:
    data = line.lower().split()
    
    if len(data) == 0:
        continue
    
    if data[0][-1] == ":":
        labels.append(data[0][:-1])
    

for line in lines:
    print line.replace("\n", "")
    
    data = line.lower().split()
    
    if len(data) == 0:
        continue
    
    if data[0][0] == "#":
        continue
    
    if data[0][-1] == ":":
        labels_loc[data[0][:-1]] = address
        continue    

    cmd = data[0]
    params = data[1:]

    if cmd == "var":
        if len(params) < 2:
            raise CompileError("At least 2 parameters are required!")
        if params[0] in variabiles:
            raise CompileError("Variabile '%s' already defined!" % params[0])
        
        val = []
        
        if params[1][0] == '"':
            i1 = line.find('"')
            i2 = line.find('"', 1)
            txt = line[i1 + 1:i1 + i2 + 2]
            end = line[i1 + i2 + 3:].split()
            if len(end) > 0:
                raise CompileError("Unexpected parameter")

            for c in txt:
                val.append(ord(c))
            
            val.append(0)

        else:
            for i in range(len(params) - 1):
                a = parse_int(params[1 + i])
            
                if a > 0xFF or a < 0:
                    raise CompileError("Variabile must be in range 0 - 255!")
                
                val.append(a)
            
        variabiles[params[0]] = val
        continue
    
    if cmd == "const":
        if len(params) <> 2:
            raise CompileError("Exactly 2 parameters are required!")
        if params[0] in constants:
            print "Redeclarating constant '%s' from 0x%04X to 0x%04X" % (params[0], constants[params[0]], parse_int(params[1]))
                    
        constants[params[0]] = parse_int(params[1])
        continue
    
    inst = ""
    if cmd == "set":
        inst = cmd_set(params)

    if cmd == "clear":
        inst = cmd_clear(params)

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

    if cmd == "err":
        inst = [0b10111111]        
    
    if len(inst) == 0:
        raise CompileError("Unknown command!")
    
    print " >\t0x%04X" % address,
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
    
    adr = labels_loc[labels_adr[loc]]
    lo = (adr & 0x00FF) >> 0
    hi = (adr & 0xFF00) >> 8
    program[loc + 0] = lo
    program[loc + 1] = hi
    
    print "\t0x%04X\t%s\t0x%04X" % (loc, labels_adr[loc], adr)
    
print "\nWriting variabiles section"    
    
for var_name in variabiles:
    variabiles_loc[var_name] = len(program)
    
    print "\t0x%04X\t%s\t" % (variabiles_loc[var_name], var_name),
    for val in variabiles[var_name]:
        print "0x%02X" % val,
        program.append(val)
    print 
    
for loc in variabiles_adr:
    adr = variabiles_loc[variabiles_adr[loc]]
    lo = (adr & 0x00FF) >> 0
    hi = (adr & 0xFF00) >> 8
    program[loc + 0] = lo
    program[loc + 1] = hi   

print "\nDefined constants (at the end of the program)"    
    
for const_name in constants:
    print "\t%s\t%d" % (const_name, constants[const_name])

print "\nDisassemble"    

pos = 0
while pos < len(program):
    cmd = program[pos] 
    
    print "0x%04X\t%02X\t" % (pos, cmd),
    
    if cmd & 0b11000000 == 0b00000000:
        map_r = {
        0b000 : 'A',
        0b001 : 'B',
        0b010 : 'C',
        0b011 : 'D',
        0b100 : 'X',
        0b101 : 'Y',
        0b110 : 'M1',
        0b111 : 'M2'}        
        
        print map_r[(cmd & 0b00111000) >> 3], "->", map_r[cmd & 0b00000111]
        
    if cmd & 0b11000000 == 0b01000000:
        map_op = {
        0b000 : 'A + B',
        0b001 : 'A + 1',
        0b010 : 'A & B',
        0b011 : 'A | B',
        0b100 : 'A ^ B',
        0b101 : '~A',
        0b110 : 'A >> 1',
        0b111 : 'NOP'}        

        map_r = {
        0b000 : 'J1',
        0b001 : 'J2',
        0b010 : 'C',
        0b011 : 'D',
        0b100 : 'X',
        0b101 : 'Y',
        0b110 : 'M1',
        0b111 : 'M2'}      
        
        print map_op[(cmd & 0b00111000) >> 3], "->", map_r[cmd & 0b00000111]
 
    if cmd & 0b11110000 == 0b10000000:
        map_s = {
        0b000 : 'PC',
        0b001 : 'INC',
        0b010 : 'J',
        0b011 : 'M',
        0b100 : 'XY',
        0b101 : '0xFFFF',
        0b110 : '0x0000',
        0b111 : '0x0000'}        
        
        map_d = {
        0b0 : 'PC',
        0b1 : 'XY'}

        print map_s[(cmd & 0b00001110) >> 1], "->", map_d[cmd & 0b00000001]
 
    if cmd & 0b11110000 == 0b10010000:
        if cmd & 0b00000111:
            if cmd & 0b00001000:
                print "if not",
            else:
                print "if",

            if cmd & 0b00000100:
                print "zero",
            if cmd & 0b00000010:
                print "overflow",
            if cmd & 0b00000001:
                print "sign",
            
            print "then",
                
        print "J -> PC"
        
    if cmd & 0b11111000 == 0b10100000:
        map_r = {
        0b000 : 'A',
        0b001 : 'B',
        0b010 : 'C',
        0b011 : 'D',
        0b100 : 'X',
        0b101 : 'Y',
        0b110 : 'M1',
        0b111 : 'M2'}        
        
        print "0x%02X" % program[pos + 1], "->", map_r[cmd & 0b00000111]
        pos += 1        
        
    if cmd & 0b11111000 == 0b10101000:
        map_r = {
        0b000 : 'A',
        0b001 : 'B',
        0b010 : 'C',
        0b011 : 'D',
        0b100 : 'X',
        0b101 : 'Y',
        0b110 : 'J1',
        0b111 : 'J2'}        
        
        print "mem(M) ->", map_r[cmd & 0b00000111]

    if cmd & 0b11111000 == 0b10110000:
        map_r = {
        0b000 : 'A',
        0b001 : 'B',
        0b010 : 'C',
        0b011 : 'D',
        0b100 : 'X',
        0b101 : 'Y',
        0b110 : '0xFF',
        0b111 : '0x00'}        
        
        print  map_r[cmd & 0b00000111], "-> mem(M)"
      
    if cmd & 0b11111100 == 0b10111000:
        map_r = {
        0b00 : 'M',
        0b01 : 'XY',
        0b10 : 'J',
        0b11 : 'AB'}        
        
        lo = program[pos + 1]
        hi = program[pos + 2]
        
        val = (hi << 8) + lo 
        
        print "0x%04X ->" % val, map_r[cmd & 0b00000011]
        pos += 2

    if cmd & 0b11111100 == 0b10111100:
        map_op = {
        0b00 : 'PC -> XY, J -> PC',
        0b01 : 'XY -> PC',
        0b10 : 'HALT',
        0b11 : 'ERROR'}        
        
        print map_op[cmd & 0b00000011]
        
    pos += 1

b.write("".join(map(chr, program)))    

f.close()
b.close()
    
