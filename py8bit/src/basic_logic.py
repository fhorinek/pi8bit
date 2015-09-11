import pygame
import cell
        
class And(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.outputs.append("Y")
        self.inputs.append("A")
        self.inputs.append("B")
        
    def calc(self, pin):
        if pin == "Y":
            return self.input("A") & self.input("B")
        
    def draw(self):
        cell.Cell.draw(self)
        self.parent.draw_text("AND", self.get_rect())    
        
class Or(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.outputs.append("Y")
        self.inputs.append("A")
        self.inputs.append("B")
       
    def calc(self, pin):
        if pin == "Y":
            return self.input("A") | self.input("B")
        
    def draw(self):
        cell.Cell.draw(self)
        self.parent.draw_text("OR", self.get_rect())      
        
class Xor(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.outputs.append("Y")
        self.inputs.append("A")
        self.inputs.append("B")

        
    def calc(self, pin):
        if pin == "Y":
            return self.input("A") ^ self.input("B")
        
    def draw(self):
        cell.Cell.draw(self)
        self.parent.draw_text("XOR", self.get_rect())     

class Not(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.outputs.append("Y")
        self.inputs.append("A")
        
    def calc(self, pin):
        if pin == "Y":
            return not self.input("A")
        
    def draw(self):
        cell.Cell.draw(self)
        self.parent.draw_text("NOT", self.get_rect())
    
        
class Nand(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.outputs.append("Y")
        self.inputs.append("A")
        self.inputs.append("B")
        
    def calc(self, pin):
        if pin == "Y":
            return not (self.input("A") & self.input("B"))
        
    def draw(self):
        cell.Cell.draw(self)
        self.parent.draw_text("NAND", self.get_rect())           
        
class Nor(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.outputs.append("Y")
        self.inputs.append("A")
        self.inputs.append("B")
        
    def calc(self, pin):
        if pin == "Y":
            return not (self.input("A") | self.input("B"))
        
    def draw(self):
        cell.Cell.draw(self)
        self.parent.draw_text("NOR", self.get_rect())                   