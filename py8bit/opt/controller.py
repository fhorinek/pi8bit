from collections import OrderedDict
from cell import High, Low

import pygame
from pygame import Rect

LEFT    = 1
MID     = 2
RIGHT   = 3
WHEEL_UP    =   4
WHEEL_DOWN  =   5

MODE_IDLE = 0
MODE_MOVE = 1
MODE_ADD  = 2
MODE_DEL  = 3
MODE_WIRE = 4


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
        self.obj_id = 0
        
        self.pan = False
        self.pan_x = 0
        self.pan_y = 0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.zoom = 1.0
        
        self.font = pygame.font.Font(pygame.font.get_default_font(), int(self.canvas.style["d_font"] * self.zoom))
        
    def get_obj_id(self):
        self.obj_id += 1
        return self.obj_id
    
    def assign_pos(self, name):
        o = self.objects[name]
        o.set_pos(self.canvas.style["d_space"], self.default_y)
        self.default_y += self.canvas.style["d_space"] + o.rect.h
        
    def normalize_positons(self):
        big_rect = False
        for k in self.objects:
            o = self.objects[k]
            if big_rect:
                big_rect = big_rect.union(o.rect)
            else:
                big_rect = o.rect
        
        offset_x = big_rect[0]
        offset_y = big_rect[1]
        
        for k in self.objects:
            o = self.objects[k]
            pos_x = o.rect[0] - offset_x
            pos_y = o.rect[1] - offset_y
            o.set_pos(pos_x, pos_y)
        
        
               
    def write_file(self, filename):
        lines = ""
        
        self.normalize_positons()
        
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
        
        try:        
            f = open(filename, "r")
            data = f.readlines()
            f.close()
            
            self.create_objects(data)
    
            print "done", filename
        except IOError:
            print "not found"

        
        
    def create_objects(self, data):
        params = OrderedDict()
        line_n = 0

        for line in data:
            line_n += 1 
            
            arr = line.split()
            
            print "%5d: %s" % (line_n, " ".join(arr))
            
            if (len(arr) < 2):
                continue
            
            name = arr[0]
            fcs = arr[1]
            
            #calc id
            s = name.split("_")
            if len(s) == 4 and s[0] == "" and s[1] == "":
                try:
                    obj_id = int(s[3])
                    self.obj_id = max(obj_id + 1, self.obj_id)
                except ValueError:
                    pass
            
            o = False
            if fcs in self.canvas.cells:
                o = self.canvas.cells[fcs](self)
             
            if (o is not False):
                params[name] = arr
                self.objects[name] = o
        
        #let object to parse parameters
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
    
    def find_output(self, obj, pin):
        for k in self.objects:
            o = self.objects[k]
            for p in o.inputs:
                pair = o.inputs[p]
                if pair == False:
                    continue
                if pair[0] == obj and pair[1] == pin:
                    return o, p
        return False
    
    def blit(self, surface, rect):
        rect = Rect(rect)
        rect.x *= self.zoom
        rect.y *= self.zoom
        rect.x += self.pan_offset_x
        rect.y += self.pan_offset_y
        self.canvas.screen.blit(surface, rect)
        
    def draw_circle(self, pos, state):
        pos = [int(x * self.zoom) for x in pos] 
        pos[0] += self.pan_offset_x
        pos[1] += self.pan_offset_y        
        if (state):
            color = self.canvas.style["c_high"]
        else:
            color = self.canvas.style["c_low"]

        self.canvas.draw_circle(color, pos, self.zoom) 
        
    def draw_line(self, start, end, state):     
        start =  [int(x * self.zoom) for x in start] 
        end = [int(x * self.zoom) for x in end] 
        
        start[0] += self.pan_offset_x
        start[1] += self.pan_offset_y
        end[0] += self.pan_offset_x
        end[1] += self.pan_offset_y
          
        if (state):
            color = self.canvas.style["c_high"]
        else:
            color = self.canvas.style["c_low"]   
            
        self.canvas.draw_line(start, end, color, self.zoom)
        
    def draw_rect(self, surface, color, rect, width = 0):
        rect = Rect(rect)
        rect.w = int(rect.w * self.zoom)
        rect.h = int(rect.h * self.zoom)
        w = int(width * self.zoom)
        if width > 0 and w == 0:
            w = 1
        pygame.draw.rect(surface, color, rect, w)
        
    def draw_text(self, surface, text, rect):
        tmp = self.font.render(text, True, self.canvas.style["c_text"])
        rect2 = tmp.get_rect()
        rect = Rect([int(x * self.zoom) for x in rect]) 
        rect = [rect.x + rect.w / 2 - rect2.w / 2, rect.y + rect.h / 2 - rect2.h / 2]
        
        surface.blit(tmp,  rect)        
        
    def mk_surface(self, rect):
        size = [int(rect.w * self.zoom), int(rect.h * self.zoom)]
        return pygame.Surface(size, self.canvas.surface_flags)
        
    def update_zoom(self):
        self.font = pygame.font.Font(pygame.font.get_default_font(), int(self.canvas.style["d_font"] * self.zoom))
        for k in self.objects:
            self.objects[k].update_body()     
        
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
            
    def request_update(self):
        pass
            
    def clear_io_cache(self):
        for k in self.objects:
            self.objects[k].clear_io_cache()              
            
    def get_object_pos(self, pos):
        pos = list(pos)
        object_list = list(self.objects.keys())
        object_list.reverse()
        for k in object_list:
            o = self.objects[k]
            if (o.rect.collidepoint(pos)):
                return o
        return False        
    
    def get_line_pos(self, pos):
        pos = list(pos)
        object_list = list(self.objects.keys())
        object_list.reverse()
        for k in object_list:
            o = self.objects[k]
            data = o.check_input_line_collision(pos)
            if (data):
                return data
        return False   
    
    def get_output_pos(self, pos):
        pos = list(pos)
        object_list = list(self.objects.keys())
        object_list.reverse()
        for k in object_list:
            o = self.objects[k]
            pin = o.check_output_collision(pos)
            if (pin):
                return o, pin
        return False   
   
    def get_input_pos(self, pos, exclude=[]):
        pos = list(pos)
        object_list = list(self.objects.keys())
        object_list.reverse()
        for k in object_list:
            if k in exclude:
                continue
            o = self.objects[k]
            pin = o.check_input_collision(pos)
            if (pin):
                return o, pin
        return False     
            
        
    def add_object(self, fcs, pos):
        o = self.canvas.cells[fcs](self)
        name = "__%s_%d" % (fcs, self.get_obj_id())
        self.objects[name] = o
        o.update()
        pos = "%dx%d" % (pos[0], pos[1])
        o.parse([name, fcs, pos])
        self.apply_grid(o)
        self.canvas.request_io_redraw() 
        return o     
           
    def apply_grid(self, obj):
        g_hor = self.canvas.style["g_hor"]
        g_ver = self.canvas.style["g_ver"]        
        obj.rect.x = int(round(obj.rect.x / float(g_hor)) * g_hor)
        obj.rect.y = int(round(obj.rect.y / float(g_ver)) * g_ver)
        obj.update_io_xy()
        
    def delete(self, name):
        if name in self.objects:
            self.objects[name].disconnect()
            del self.objects[name]
            
        #TODO: remove orphan wire nodes

            
    def event(self, event, mode):
        if hasattr(event, "pos"):
            mouse_x = (event.pos[0] - self.pan_offset_x) / self.zoom
            mouse_y = (event.pos[1] - self.pan_offset_y) / self.zoom  
        
        #PAN is allways working
        if event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT:
            self.pan = False
            self.pan_offset_x += event.pos[0] - self.pan_x
            self.pan_offset_y += event.pos[1] - self.pan_y        
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT:
            self.pan = True
            self.pan_x = event.pos[0]
            self.pan_y = event.pos[1]
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == WHEEL_UP:   
            self.zoom += 0.1
            self.update_zoom()
            self.canvas.request_io_redraw()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == WHEEL_DOWN:   
            if self.zoom > 0.1:
                self.zoom -= 0.1
                self.update_zoom()
                self.canvas.request_io_redraw()
       
            
        if event.type == pygame.MOUSEMOTION:
            if self.pan:
                self.pan_offset_x += event.pos[0] - self.pan_x
                self.pan_offset_y += event.pos[1] - self.pan_y     
                self.pan_x = event.pos[0]
                self.pan_y = event.pos[1]
                self.canvas.request_io_redraw()                    
        
        if mode == MODE_IDLE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                o = self.get_object_pos([mouse_x, mouse_y])
                if o is not False:
                    o.click()
         
        if mode == MODE_DEL:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                o = self.get_object_pos([mouse_x, mouse_y])
                if o:
                    self.delete(o.name)
                    self.canvas.request_io_redraw()
                    self.canvas.reset_mode()
                else:
                    w = self.get_line_pos([mouse_x, mouse_y])
                    if w:
                        o = w[0]
                        p = w[1]
                        o.clear_input(p)
                        self.canvas.request_io_redraw()
                        self.canvas.reset_mode()                        
             
        if mode == MODE_ADD:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                fcs = self.canvas.cells.keys()[self.canvas.add_cell_index]
                self.add_object(fcs, [mouse_x, mouse_y])   
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                self.canvas.inc_cell_index()        

            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self.canvas.dec_cell_index()        
                
        if mode == MODE_WIRE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                start = self.get_output_pos([mouse_x, mouse_y])
                if start is not False:
                    p = self.canvas.style["d_point"]

                    self.move = self.add_object("wire", [mouse_x + 2*p, mouse_y + 2*p])
                    self.move.assign_input("A", start[0], start[1])

                    self.move_offest = [2 * p + self.pan_offset_x, 2 * p + self.pan_offset_y]
                else:
                    w = self.get_line_pos([mouse_x, mouse_y])
                    if w:
                        in_cell = w[0]
                        in_pin = w[1]
                        out_cell = w[2]
                        out_pin = w[3]
                        
                        p = self.canvas.style["d_point"]
    
                        self.move = self.add_object("wire", [mouse_x + 2*p, mouse_y + 2*p])
                        self.move.assign_input("A", out_cell, out_pin)
                        in_cell.assign_input(in_pin, self.move, "Y")
    
                        self.move_offest = [2 * p + self.pan_offset_x, 2 * p + self.pan_offset_y]                        
                        
                        

            if event.type == pygame.MOUSEMOTION:
                if self.move is not False:
                    self.move.set_pos(mouse_x, mouse_y)
                    self.canvas.request_io_redraw()

            if event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
                if self.move is not False:
                    end = self.get_input_pos([mouse_x, mouse_y], exclude = [self.move.name])
                    if end is not False:
                        obj_input = self.move.inputs["A"]
                        end[0].assign_input(end[1], obj_input[0], obj_input[1])
                        self.delete(self.move.name)
                    else:
                        self.apply_grid(self.move)
                        self.move.done_drag()   
                        
                    self.move = False
                    self.canvas.request_io_redraw()
                   
                    
        if mode == MODE_MOVE:           
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                self.move = self.get_object_pos([mouse_x, mouse_y])
                if self.move is not False:
                    self.move_offest = [mouse_x - self.move.rect[0], mouse_y - self.move.rect[1]]
        
            if event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
                if self.move is not False:
                    x = mouse_x - self.move_offest[0]
                    y = mouse_y - self.move_offest[1]                    
                    self.move.set_pos(x, y)
                    self.apply_grid(self.move)
                    self.move.done_drag()
                    self.canvas.request_io_redraw()
                self.move = False
        
            if event.type == pygame.MOUSEMOTION:
                if self.move is not False:
                    x = mouse_x - self.move_offest[0]
                    y = mouse_y - self.move_offest[1]
                    self.move.set_pos(x, y)
                    self.canvas.request_io_redraw()
                
