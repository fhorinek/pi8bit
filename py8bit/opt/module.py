from cell import Cell
from controller import Controller
from pygame import Rect
from utils import file_opendialog
import os

class module(Cell, Controller):
    def __init__(self, parent):
        Cell.__init__(self, parent)
        Controller.__init__(self, self.parent.canvas, parent)
        self.offset_x = 0
        self.offset_y = 0
        self.update_request = False
        
    def get_params(self):
        arr = Cell.get_params(self)
        return [arr[0], self.filename] + arr[1:]
        
    def calc(self, pin):
        return self.objects[pin].input("A")
        
    def parse_cfg(self, arr):
        if len(arr) < 4:
            path = file_opendialog("inc")

            arr.append(path)
            
        self.filename = arr[3]
        self.read_file(self.filename)
        
        for k in self.objects:
            o = self.objects[k]
            if o.fcs == "output":
                self.add_output(k)
            if o.fcs == "input":
                self.add_input(k)    
                o.set_module(self)
                
            o.drawable = True
    
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
    
    def draw_line(self, start, end, state):
        start = [self.rect.x + start[0] + self.offset_x, self.rect.y + start[1] + self.offset_y]
        end = [self.rect.x + end[0] + self.offset_x, self.rect.y + end[1] + self.offset_y]
        self.parent.draw_line(start, end, state)
    
    def draw_circle(self, pos, state):
        pos = [self.rect.x + pos[0] + self.offset_x, self.rect.y + pos[1] + self.offset_y]
        self.parent.draw_circle(pos, state) 
    
    def blit(self, surface, rect):
        rect = Rect(rect)
        rect.x += self.offset_x
        rect.y += self.offset_y
        rect.x *= self.zoom
        rect.y *= self.zoom   
        self.surface.blit(surface, rect)
    
    def draw(self):
        if (self.update_request):
            self.update_request = False
            self.update_body()
            self.clear_io_cache()
            
        Cell.draw(self)
        
    def draw_io(self):
        Cell.draw_io(self)
        
        if not self.drawable:
            return

        for k in self.objects:
            self.objects[k].draw_io()
    
    def update_body(self, state=None):
        self.zoom = self.parent.zoom
        self.font = self.parent.font
        self.label_font = self.parent.label_font
        
        Cell.update_body(self, state=state)
        for k in self.objects:
            self.objects[k].update_body()
            self.objects[k].draw()
            
        #update_request is invalid since all cell were allready redrawn (and it is triggered by Cell.update_body())
        self.update_request = False
            
    def request_update(self):
        self.update_request = True
    
    def set_pos(self, x, y):
        Cell.set_pos(self, x, y)
        self.update_rect()
        
    def clear_io_cache(self):
        Cell.clear_io_cache(self)
        Controller.clear_io_cache(self)
        
class minput(Cell):
    def __init__(self, parent):
        Cell.__init__(self, parent)
        self.add_output("Y")
        self.val = 0
        self.old_value = 0
        self.module = None
        
    def set_module(self, module):
        self.module = module
        
    def calc(self, pin):
        if self.module is not None:
            self.val = self.module.input(self.name)
            
        if (self.old_value is not self.val):
            self.old_value = self.val
            self.update_body()       
                 
        return self.val
        
    def click(self):
        if self.module is None:
            self.val = not self.val
            self.update_body()       
        
    def update_body(self, state=None):
        Cell.update_body(self, state=self.val)
        self.parent.draw_text(self.surface, self.name, self.rect_rel)
        
class moutput(Cell):
    def __init__(self, parent):
        Cell.__init__(self, parent)
        self.add_input("A")
        self.old_value = 0
        
    def tick(self):
        if (self.old_value is not self.input("A")):
            self.old_value = self.input("A")
            self.update_body()
                    
    def update_body(self, state=None):
        Cell.update_body(self, state=self.input("A"))
        self.parent.draw_text(self.surface, self.name, self.rect_rel)        