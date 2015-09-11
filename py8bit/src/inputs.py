import pygame
import cell

class Constant(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.val = 0
        
        self.outputs.append("Y")

    def parse(self, arr):
        if len(arr) == 5:
            self.val = int(arr[4])

    def calc(self, pin):
        if pin == "Y":
            return self.val
        
    def draw(self):
        if (self.val):
            color = self.parent.c_high
        else:
            color = self.parent.c_low
        cell.Cell.draw(self, color)        
        self.parent.draw_text("const", self.get_rect())
        
class Toggle(Constant):
    def click(self):
        self.val = not self.val
        
    def draw(self):
        if (self.val):
            color = self.parent.c_high
        else:
            color = self.parent.c_low
        cell.Cell.draw(self, color)        
        self.parent.draw_text("Toggle", self.get_rect())   