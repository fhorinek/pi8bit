from collections import OrderedDict
from cell import High, Low

import pygame

LEFT = 1
RIGHT = 3

class Controller():
    def __init__(self, canvas, parent):
        self.canvas = canvas
        self.parent = parent

        self.objects = OrderedDict()
        self.objects["LOW"] = Low(self)
        self.objects["HIGH"] = High(self)
        

        
        self.move = False
        self.move_offest = False
        
        self.default_y = 0
    
    def assign_pos(self, name):
        o = self.objects[name]
        o.set_pos(10, self.default_y)
        self.default_y += 10 + o.rect.h
        
    def write_file(self, filename):
        lines = ""
        for k in self.objects:
            if k in ["HIGH", "LOW"]:
                continue
            o = self.objects[k]
            
            name = o.name
            fcs = o.fcs
            params = " ".join(o.get_params())
            line = name, fcs, params
            lines += "%s\n" % "\t".join(line)
        
        f = open(filename, "w")
        f.write(lines)
        f.close() 
        
        
    def read_file(self, filename):
        print "Reading file", filename
                
        f = open(filename, "r")
        data = f.readlines()
        f.close()
        
        self.create_objects(data)

        print "done", filename
        
    def create_objects(self, data):
        params = OrderedDict()
        line_n = 0

        for line in data:
            line_n += 1 
            
            arr = line.split()
            
            print "%5d: %s" % (line_n, " ".join(arr))
            
            name = arr[0]
            fcs = arr[1]

            o = False
            if fcs in self.canvas.cells:
                o = self.canvas.cells[fcs](self)
             
            if (o is not False):
                params[name] = arr
                self.objects[name] = o
        
        for name in params:
            arr = params[name]

            o = self.objects[name]
            o.parse(arr)   
    
    def find_cell_pin(self, name):
       
        arr = name.split(".")
        if (len(arr) == 1):
            o_name = arr[0]
            o_pin = False
        else:
            o_name, o_pin = arr
        
        o = self.objects[o_name]
        if not o_pin:
            o_pin = o.outputs[0]
        
        return o, o_pin  
    
    def blit(self, surface, rect):
        self.canvas.screen.blit(surface, rect)
        
    def draw_circle(self, pos, state):
        if (state):
            color = self.canvas.style["c_high"]
        else:
            color = self.canvas.style["c_low"]

        pygame.draw.circle(self.canvas.screen, color, pos, self.canvas.style["d_point"]) 
        
    def draw_line(self, start, end, state):       
        if (state):
            color = self.canvas.style["c_high"]
        else:
            color = self.canvas.style["c_low"]   
            
        self.canvas.draw_line(start, end, color)
        
    def draw(self):
        for k in self.objects:
            self.objects[k].draw()
            self.objects[k].draw_io()
        
    def tick(self):
        for k in self.objects:
            self.objects[k].tick()        
        
    def reset(self):
        for k in self.objects:
            self.objects[k].reset()     
            
    def get_object_pos(self, pos):
        object_list = list(self.objects.keys())
        object_list.reverse()
        for k in object_list:
            o = self.objects[k]
            if (o.rect.collidepoint(pos)):
                return o
        return False            
            
    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
            o = self.get_object_pos(event.pos)
            if o is not False:
                o.click()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT:
            self.move = self.get_object_pos(event.pos)
            if self.move is not False:
                self.move_offest = [event.pos[0] - self.move.rect[0], event.pos[1] - self.move.rect[1]]
                
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT:
            if self.move is not False:
                g_hor = self.canvas.style["g_hor"]
                g_ver = self.canvas.style["g_ver"]
                x = int(round((event.pos[0] - self.move_offest[0]) / float(g_hor)) * g_hor)
                y = int(round((event.pos[1] - self.move_offest[1]) / float(g_ver)) * g_ver)
                self.move.set_pos(x, y)
            self.move = False
        
        if event.type == pygame.MOUSEMOTION:
            if self.move is not False:
                x = event.pos[0] - self.move_offest[0]
                y = event.pos[1] - self.move_offest[1]
                self.move.set_pos(x, y)