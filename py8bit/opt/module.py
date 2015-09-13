from cell import Cell
from controller import Controller
from pygame import Rect

class module(Cell, Controller):
    def __init__(self, parent):
        Cell.__init__(self, parent)
        Controller.__init__(self, self.parent.canvas, parent)
        self.offset_x = 0
        self.offset_y = 0
        
    def get_params(self):
        arr = Cell.get_params(self)
        return [arr[0], self.filename] + arr[1:]
        
    def calc(self, pin):
        return self.objects[pin].input("A")
        
    def parse_cfg(self, arr):
        self.filename = arr[3]
        self.read_file(self.filename)
        
        for k in self.objects:
            o = self.objects[k]
            if o.fcs == "output":
                self.add_output(k)
            if o.fcs == "input":
                self.add_input(k)    
                o.set_module(self)   
    
        del arr[3]
        Cell.parse_cfg(self, arr)
    
    def tick(self):
        Controller.tick(self)
        Cell.tick(self)
             

    def update_rect(self):
        rect = Rect(0, 0, 0, 0)
        for k in self.objects:
            o = self.objects[k]
            rect = rect.union(o.rect)
            
        self.rect.w = rect.w + self.canvas.style["d_space"] * 2
        self.rect.h = rect.h + self.canvas.style["d_space"] * 2

        self.offset_x = self.canvas.style["d_space"]
        self.offset_y = self.canvas.style["d_space"]
        
        if len(self.inputs) > 1:
            self.rect.w += self.parent.canvas.style["d_input"]
            self.offset_x += self.parent.canvas.style["d_input"]

        if len(self.outputs) > 1:
            self.rect.w += self.parent.canvas.style["d_output"]

        self.rect_rel = Rect(self.rect)
        self.rect_rel.x = 0
        self.rect_rel.y = 0
        self.update_io_xy()
    
    def blit(self, surface, rect):
        rect.x += self.offset_x
        rect.y += self.offset_y
        self.surface.blit(surface, rect)
    
    def draw(self):
        Cell.draw(self)
        for k in self.objects:
            self.objects[k].draw_io()
    
    def update_body(self, state=None):
        Cell.update_body(self, state=state)
        for k in self.objects:
            self.objects[k].draw()
    
    def set_pos(self, x, y):
        dx = x - self.rect.x
        dy = y - self.rect.y
        Cell.set_pos(self, x, y)
        for k in self.objects:
            o = self.objects[k]
            x = o.rect.x + dx
            y = o.rect.y + dy  
            o.set_pos(x, y)
        
class minput(Cell):
    def __init__(self, parent):
        Cell.__init__(self, parent)
        self.add_output("Y")
        
    def set_module(self, module):
        self.module = module
        
    def calc(self, pin):
        return self.module.input(self.name)
        
    def update_body(self, state=None):
        Cell.update_body(self, state=state)
        self.draw_text(self.name, self.rect_rel)
        
class moutput(Cell):
    def __init__(self, parent):
        Cell.__init__(self, parent)
        self.add_input("A")
        
    def update_body(self, state=None):
        Cell.update_body(self, state=state)
        self.draw_text(self.name, self.rect_rel)        