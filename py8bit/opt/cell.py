import pygame
from collections import OrderedDict
from pygame.rect import Rect

class Cell():
    def __init__(self, parent):
        self.parent = parent
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.rect_rel = pygame.Rect(0, 0, 0, 0)
        self.input_xy = OrderedDict()
        self.output_xy = OrderedDict()
        
        self.inputs = OrderedDict()
        self.outputs = []
        
        self.res = {}
        self.name = "cell"    
        self.fcs = "cell"    
            
    def add_input(self, name):
        self.inputs[name] = False
    
    def add_output(self, name):
        self.outputs.append(name)
                
    def update_rect(self): 
        self.rect.w = self.parent.canvas.style["d_width"]
        
        h = max((len(self.inputs), len(self.outputs)))
        self.rect.h = self.parent.canvas.style["d_line"] * h
        
        if len(self.inputs) > 1:
            self.rect.w += self.parent.canvas.style["d_input"]

        if len(self.outputs) > 1:
            self.rect.w += self.parent.canvas.style["d_output"]

        self.rect_rel = Rect(self.rect)
        self.rect_rel.x = 0
        self.rect_rel.y = 0
        self.update_io_xy()

    def update_io_xy(self):
        for pin in self.inputs:
            i = self.inputs.keys().index(pin)
            x = self.rect.x
            y = int(self.rect.y + self.parent.canvas.style["d_line"] * (i + 0.5))
            self.input_xy[pin] = [x, y]      
            
        for pin in self.outputs:
            i = self.outputs.index(pin)
            x = self.rect.x + self.rect.w
            y = int(self.rect.y + self.parent.canvas.style["d_line"] * (i + 0.5))    
            self.output_xy[pin] = [x, y]       

    def get_input_rect(self, pin):
        i = self.inputs.keys().index(pin)
        x = 0
        y = self.parent.canvas.style["d_line"] * i
        w = self.parent.canvas.style["d_input"]
        h = self.parent.canvas.style["d_line"]
        return pygame.Rect((x, y, w, h))
    
    def get_output_rect(self, pin):
        i = self.outputs.index(pin)
        x = self.rect.w - self.parent.canvas.style["d_output"]
        y = self.parent.canvas.style["d_line"] * i
        w = self.parent.canvas.style["d_output"]
        h = self.parent.canvas.style["d_line"]
        return pygame.Rect((x, y, w, h))    

    def set_pos(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.update_io_xy()
        
    def assign_input(self, name, in_cell, in_pin):
        if name in self.inputs:
            self.inputs[name] = [in_cell, in_pin]

    def assign_free_input(self, in_cell, in_pin):
        for pin in self.inputs:
            if self.inputs[pin] == False:
                self.assign_input(pin, in_cell, in_pin)
                return
            
    def parse_cfg(self, arr):
        for i in range(len(arr) - 3):
            name =  arr[3 + i]
            conn = self.parent.find_cell_pin(name)    
            self.assign_free_input(*conn)
 
    def get_params(self):
        p = [] 
        p.append("%dx%d" % (self.rect.x, self.rect.y))

        for k in self.inputs:
            if self.inputs[k] is not False:
                o, o_pin = self.inputs[k]
                p.append("%s.%s" % (o.name, o_pin))
            else:
                p.append("LOW.Y")
        
        return p 
                        
    def parse(self, arr):
        self.name = arr[0]
        self.fcs = arr[1]
        self.parse_cfg(arr)
        self.update_rect()  
        self.update_body()
        try:
            x,y = map(int, arr[2].split("x"))
            self.set_pos(x, y)
        except:
            self.parent.assign_pos(self.name)
        
    def reset(self):
        self.res = {}
    
    def calc(self, pin):
        return 0
    
    def tick(self):
        for i in self.outputs:
            self.res[i] = self.calc(i) 
    
    def output(self, pin):
        if pin not in self.res:
            return 0
        return self.res[pin]
    
    def input(self, pin):
        if pin not in self.inputs:
            return 0
        
        if self.inputs[pin] is False:
            return 0
            
        in_obj, in_pin = self.inputs[pin]
        if in_obj is None:
            return in_pin
        else:
            return in_obj.output(in_pin)
           
    def click(self):
        pass          
    
    def update(self):
        self.update_rect()
        self.update_body()

    def draw_text(self, text, rect):
        tmp = self.parent.canvas.font.render(text, True, self.parent.canvas.style["c_text"])
        rect2 = tmp.get_rect();
        rect = [rect.x + rect.w / 2 - rect2.w / 2, rect.y + rect.h / 2 - rect2.h / 2]
        
        self.surface.blit(tmp,  rect)
    
    def update_body(self, state = None):
        size = [self.rect.w + 1, self.rect.h + 1]
        rect = Rect(0, 0, self.rect.w, self.rect.h)
        
        self.surface = pygame.Surface(size)
        if state is None:
            color = "c_fill"
        else:
            if state:
                color = "c_high"
            else:
                color = "c_low"
                
        pygame.draw.rect(self.surface, self.parent.canvas.style[color], rect)
        pygame.draw.rect(self.surface, self.parent.canvas.style["c_border"], rect, 2)
        
        if len(self.inputs) > 1:
            in_rect = Rect(0, 0, self.parent.canvas.style["d_input"], self.rect.h) 
            pygame.draw.rect(self.surface, self.parent.canvas.style["c_border"], in_rect, 1)
            
        if len(self.outputs) > 1:
            a = self.parent.canvas.style["d_output"]
            out_rect = Rect(self.rect.w - a, 0, a, self.rect.h) 
            pygame.draw.rect(self.surface, self.parent.canvas.style["c_border"], out_rect, 1)
 
        if len(self.inputs) > 1:
            for c in self.inputs:
                rect = self.get_input_rect(c)
                self.draw_text(c, rect)

        if len(self.outputs) > 1:
            for c in self.outputs:
                rect = self.get_output_rect(c)
                self.draw_text(c, rect)
 
 
     
    
    def draw(self):
        self.parent.blit(self.surface, self.rect)
    
    def draw_io(self):    
        for c in self.inputs:
            state = self.input(c)
            pos_xy = self.input_xy[c]
            self.parent.draw_circle(pos_xy, state)
              
            if self.inputs[c] is not False:
                in_obj, in_pin = self.inputs[c]
                if not isinstance(in_obj, Invisible):
                    start = pos_xy
                    end = in_obj.output_xy[in_pin]
                    self.parent.draw_line(start, end, state) 
        
        for c in self.outputs:
            state = self.output(c)
            pos_xy = self.output_xy[c]
            self.parent.draw_circle(pos_xy, state)
              
     
        
        
    
class Invisible(Cell):
    def __init__(self, parent):
        Cell.__init__(self, parent)
        self.add_output("Y")
    
    def draw(self):
        pass
    
    def draw_io(self):
        pass

class High(Invisible):
    def __init__(self, parent):
        Invisible.__init__(self, parent)
        self.name = "HIGH"
    
    def calc(self, pin):
        return 1
    
class Low(Invisible):
    def __init__(self, parent):
        Invisible.__init__(self, parent)
        self.name = "LOW"
        
    def calc(self, pin):
        return 0    