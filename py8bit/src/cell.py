import pygame

class Cell():
    def __init__(self, parent, rect):
        self.parent = parent
        self.x = rect[0] 
        self.y = rect[1]
        self.inputs = []
        self.inputs_ref = {}
        self.outputs = []
        self.res = {}
        self.res_old = {}
        self.recursion = False
        
    def set_pos(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        
    def get_rect(self):
        w = self.parent.d_width
        
        if len(self.inputs) > 0:
            w += self.parent.d_input            
        if len(self.outputs) > 0:
            w += self.parent.d_output 
            
        i = max(len(self.outputs), len(self.inputs))
        h = i * self.parent.d_line           
        
        return pygame.Rect((self.x, self.y, w, h))
        
    def get_input_xy(self, pin):
        i = self.inputs.keys().index(pin)
        x = self.x
        y = int(self.y + self.parent.d_line * (i + 0.5))
        return (x, y)        
        
    def get_input_rect(self, pin):
        i = self.inputs.index(pin)
        x = self.x
        y = self.y + self.parent.d_line * i
        w = self.parent.d_input
        h = self.parent.d_line
        return pygame.Rect((x, y, w, h))
    
    def get_output_rect(self, pin):
        i = self.outputs.index(pin)
        rect = self.get_rect()
        x = self.x + rect[2] - self.parent.d_output
        y = self.y + self.parent.d_line * i
        w = self.parent.d_output
        h = self.parent.d_line
        return pygame.Rect((x, y, w, h))    
    
    def get_output_xy(self, pin):
        i = self.outputs.index(pin)
        rect = self.get_rect()
        x = self.x + rect[2]
        y = int(self.y + self.parent.d_line * (i + 0.5))
        return (x, y)        
        
    def set_input(self, pin, in_cell, in_pin):
        self.inputs_ref[pin] = [in_cell, in_pin]
    
    def reset(self):
        self.res_old = self.res
        self.res = {}
    
    def calc(self):
        return 0
    
    def output(self, pin):
        if self.recursion:
            if pin in self.res_old: 
                return self.res_old[pin]
            else:
                return 0
        
        if pin not in self.res:
            self.recursion = True
            self.res[pin] = self.calc(pin)
            self.recursion = False
        return self.res[pin]
        
    
    def input(self, pin):
        if pin not in self.inputs_ref:
            return 0
            
        in_obj, in_pin = self.inputs_ref[pin]
        return in_obj.output(in_pin)
           
    def click(self):
        pass       
           
    def draw(self):
        pygame.draw.rect(self.parent.screen, self.parent.c_fill, self.get_rect())
        pygame.draw.rect(self.parent.screen, self.parent.c_border, self.get_rect(), 2)
        
        if len(self.inputs) > 0:
            rect = self.get_rect()
            rect[2] = self.parent.d_input  
            pygame.draw.rect(self.parent.screen, self.parent.c_border, rect, 1)
            
        if len(self.outputs) > 0:
            rect = self.get_rect()
            rect[0] += rect[2] - self.parent.d_output 
            rect[2] = self.parent.d_output 
            pygame.draw.rect(self.parent.screen, self.parent.c_border, rect, 1)
            
        for c in self.inputs:
            rect = self.get_input_rect(c)
            self.parent.draw_text(c, rect)
            x = rect[0]
            y = rect[1] + rect[3] / 2
            if (self.input(c)):
                color = self.parent.c_high
            else:
                color = self.parent.c_low
            pygame.draw.circle(self.parent.screen, color, (x, y), 5)
            
            if c in self.inputs_ref:
                in_obj, in_pin = self.inputs_ref[c]
                start = (x, y)
                end = in_obj.get_output_xy(in_pin)
                self.parent.draw_line(start, end, color) 
            
        for c in self.outputs:
            rect = self.get_output_rect(c)
            self.parent.draw_text(c, rect)
            x = rect[0] + rect[2]
            y = rect[1] + rect[3] / 2
            if (self.output(c)):
                color = self.parent.c_high
            else:
                color = self.parent.c_low
            pygame.draw.circle(self.parent.screen, color, (x, y), 5) 

        