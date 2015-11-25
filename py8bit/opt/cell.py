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
        
        self.output_cache = {}
        self.input_cache = {}
        self.res = {}
        
        self.name = "cell"    
        self.fcs = "cell"    
            
    def done_drag(self):
        pass
            
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
        
    def clear_input(self, name):
        self.inputs[name] = False
        
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
    
    def clear_io_cache(self):
        self.input_cache = {}
        self.output_cache = {}
        
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
        rect2 = tmp.get_rect()
        rect = [rect.x + rect.w / 2 - rect2.w / 2, rect.y + rect.h / 2 - rect2.h / 2]
        
        self.surface.blit(tmp,  rect)
    
    def update_body(self, state = None):
        size = [self.rect.w + 1, self.rect.h + 1]
        rect = Rect(0, 0, self.rect.w, self.rect.h)
        
        self.surface = pygame.Surface(size, self.parent.canvas.surface_flags)
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
 
        self.parent.request_update()
    
    def draw(self):
        self.parent.blit(self.surface, self.rect)
    
    def draw_io(self):   
        for c in self.inputs:
            state = self.input(c)
            if c in self.input_cache:
                if self.input_cache[c] == state:
                    continue
            
            self.input_cache[c] = state
                
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
            if c in self.output_cache:
                if self.output_cache[c] == state:
                    continue
            
            self.output_cache[c] = state       
                 
            pos_xy = self.output_xy[c]
            self.parent.draw_circle(pos_xy, state)
             
    def check_output_collision(self, pos):
        for pin in self.outputs:
            if pin in self.output_xy:
                out_pos = self.output_xy[pin]
                p = self.parent.canvas.style["d_point"]
                rect = pygame.Rect(out_pos[0] - p, out_pos[1] - p, p * 2, p * 2)
                if (rect.collidepoint(pos)):
                    return pin
        return False
    
    def check_input_collision(self, pos):
        for pin in self.inputs:
            if pin in self.input_xy:
                out_pos = self.input_xy[pin]
                p = self.parent.canvas.style["d_point"]
                rect = pygame.Rect(out_pos[0] - p, out_pos[1] - p, p * 2, p * 2)
                if (rect.collidepoint(pos)):
                    return pin
        return False    
     
    def check_input_line_collision(self, pos):
        for p in self.inputs:
            if self.inputs[p]:
                obj, pin = self.inputs[p]
                if isinstance(obj, Invisible):
                    continue

                start = self.input_xy[p]
                end = obj.output_xy[pin]
                #basic rect TODO
                offset = self.parent.canvas.style["d_line_col"]
                
                x = min((start[0], end[0])) - offset
                y = min((start[1], end[1])) - offset
                w = abs(start[0] - end[0]) + offset * 2
                h = abs(start[1] - end[1]) + offset * 2
                
                basic = Rect(x, y, w, h)
                
                if basic.collidepoint(pos):
                
                    dx = end[0] - start[0]
                    dy = end[1] - start[1]
                    if abs(dx) < abs(dy):
                        k = float(dx) / float(dy)
                        x = start[0] + k * (pos[1] - start[1])
                
                        if abs(x - pos[0]) < offset:
                            return self, p, obj, pin                      
                    else:
                        k = float(dy) / float(dx)
                        y = start[1] + k * (pos[0] - start[0])
                        
                        if abs(y - pos[1]) < offset:
                            return self, p, obj, pin
        return False 
    
    def disconnect(self):
        for wire_output in self.outputs:
            print wire_output
            while True:
                target = self.parent.find_output(self, wire_output)
                if target:
                    target[0].clear_input(target[1])
                else:
                    break
        
      
class Wire(Cell):
    def __init__(self, parent):
        Cell.__init__(self, parent)
        self.add_input("A")
        self.add_output("Y")
        
    def get_parent(self):
        obj, pin = self.inputs["A"]
#         while (obj.fcs == "wire"):
#             obj, pin = obj.inputs["A"]
            
        return obj, pin
        
    def update_rect(self):
        self.rect.w = self.parent.canvas.style["d_wire_col"]
        self.rect.h = self.parent.canvas.style["d_wire_col"]
        
    def update_io_xy(self):
        x = self.rect.x + self.parent.canvas.style["d_wire_col"] / 2
        y = self.rect.y + self.parent.canvas.style["d_wire_col"] / 2
        self.input_xy["A"] = [x, y]
        self.output_xy["Y"] = [x, y]
        
    def done_drag(self):
        Cell.done_drag(self)
        
    def set_pos(self, x, y):
        Cell.set_pos(self, x, y)
        
    def update_body(self, state=None):
        pass
     
    def draw(self):
        pass  
    
    def calc(self, pin):
        return self.input("A")
        
               
    
class Invisible(Cell):
    def __init__(self, parent):
        Cell.__init__(self, parent)
        self.add_output("Y")
    
    def update_body(self, state=None):
        pass
    
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
    
