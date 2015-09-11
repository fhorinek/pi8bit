import cell
import pygame

class HexDisplay(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.inputs.append("A0")
        self.inputs.append("A1")
        self.inputs.append("A2")
        self.inputs.append("A3")
        self.inputs.append("A4")
        self.inputs.append("A5")
        self.inputs.append("A6")
        self.inputs.append("A7")
        
    def draw(self):
        cell.Cell.draw(self)
        
        val  = self.input("A0") * 1
        val += self.input("A1") * 2
        val += self.input("A2") * 4
        val += self.input("A3") * 8
        val += self.input("A4") * 16
        val += self.input("A5") * 32
        val += self.input("A6") * 64
        val += self.input("A7") * 128
                
        self.parent.draw_text("%02X" % val, self.get_rect())
        
class Led(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.inputs.append("A")
        
    def draw(self):
        if (self.input("A")):
            color = self.parent.c_high
        else:
            color = self.parent.c_low
        cell.Cell.draw(self, color)
        self.parent.draw_text("%d" % self.input("A"), self.get_rect())
