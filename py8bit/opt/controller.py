from collections import OrderedDict
from cell import High, Low, Invisible

import wire
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
MODE_PAN  = 5
MODE_SELECT = 6
MODE_EDIT = 7


class Controller():
    def __init__(self, canvas, parent):
        self.canvas = canvas
        self.parent = parent

        self.objects = OrderedDict()
        self.objects["LOW"] = Low(self)
        self.objects["HIGH"] = High(self)
        
        self.selected = []
        self.select = False
        self.select_start = False
        self.select_rect = Rect(0, 0, 0, 0)
        
        self.possible_move = False
        
        self.pan = False
        self.pan_x = 0
        self.pan_y = 0
        self.pan_offset_x = 0
        self.pan_offset_y = 0

        self.new_node = False

        self.zoom = 1.0
        
        self.obj_id = 0
        self.net_id = 0
        
        self.font = pygame.font.Font(pygame.font.get_default_font(), int(self.canvas.style["d_font"] * self.zoom))
        
    def get_obj_id(self):
        self.obj_id += 1
        return self.obj_id
    
    def get_net_id(self):
        self.net_id += 1
        return self.net_id    
        
    def normalize_positons(self):
        big_rect = False
        for k in self.objects:
            o = self.objects[k]
            if not isinstance(o, Invisible):
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
            p = o.get_params()
            if p == False:
                continue
            params = " ".join(p)
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
            
            #calc obj id
            s = name.split("_")
            if len(s) == 4 and s[0] == "" and s[1] == "":
                try:
                    obj_id = int(s[3])
                    self.obj_id = max(obj_id + 1, self.obj_id)
                except ValueError:
                    pass

            #calc net id
            if fcs == "node":
                s = arr[3].split("_")
                if len(s) == 4 and s[0] == "" and s[1] == "":
                    try:
                        net_id = int(s[3])
                        self.obj_id = max(net_id + 1, self.net_id)
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
            
    def find_cell(self, name):
        if name in self.objects:
            return self.objects[name]
        else:
            return False           
            
    def find_cell_pin(self, name):
        arr = name.split(".")
        if (len(arr) == 1):
            o_name = arr[0]
            o_pin = False
        else:
            o_name, o_pin = arr
        
        o = self.find_cell(o_name)
        if o == False:
            return False
        
        if o_pin == False:
            if len(o.outputs) > 0:
                o_pin = o.outputs[0]
            else:
                o_pin = False
        
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
          
        if state:
            color = self.canvas.style["c_high"]
        else:
            color = self.canvas.style["c_low"]   
            
        self.canvas.draw_line(start, end, color, self.zoom)
        
    def draw_rect(self, surface, color, rect, width = 0):
        rect = Rect(rect)
        w = int(width * self.zoom)
        rect = Rect([int(x * self.zoom) for x in rect]) 
        if width > 0 and w == 0:
            w = 1
        pygame.draw.rect(surface, color, rect, w)
        
    def draw_text(self, surface, text, rect):
        tmp = self.font.render(text, True, self.canvas.style["c_text"])
        rect2 = tmp.get_rect()
        rect = Rect([int(x * self.zoom) for x in rect]) 
        rect = [rect.x + rect.w / 2 - rect2.w / 2, rect.y + rect.h / 2 - rect2.h / 2]
        
        surface.blit(tmp,  rect)        
        
    def draw_highlight(self, rect):
        rect = Rect(rect)
        width = self.canvas.style["d_line_height"]
        w = int(width * self.zoom)
        rect = Rect([int(x * self.zoom) for x in rect]) 
        rect.x += self.pan_offset_x
        rect.y += self.pan_offset_y
        if width > 0 and w == 0:
            w = 1
        pygame.draw.rect(self.canvas.surface_io, self.canvas.style["c_highlight"], rect, w)
         
    def mk_surface(self, rect):
        size = [int(rect.w * self.zoom), int(rect.h * self.zoom)]
        return pygame.Surface(size, self.canvas.surface_flags)
        
    def update_zoom(self):
        self.font = pygame.font.Font(pygame.font.get_default_font(), int(self.canvas.style["d_font"] * self.zoom))
        for k in self.objects:
            self.objects[k].update_body()     
        
    def draw(self, mode):
        if mode == MODE_SELECT:
            self.canvas.request_io_redraw()
        
        for k in self.objects:
            self.objects[k].draw()
            self.objects[k].draw_io()

        if mode == MODE_SELECT:
            self.select_rect.normalize()
            self.draw_highlight(self.select_rect)
        
        for o in self.selected:
            self.draw_highlight(o.rect)
        
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
            
    def get_object_pos(self, pos, exclude = []):
        pos = list(pos)
        object_list = list(self.objects.keys())
        object_list.reverse()
        for k in object_list:
             
            o = self.objects[k]
            if o in exclude:
                continue               
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
    
    def get_output_pos(self, pos, exclude=[]):
        pos = list(pos)
        object_list = list(self.objects.keys())
        object_list.reverse()
        for k in object_list:
            o = self.objects[k]
            if o in exclude:
                continue            
            
            pin = o.check_output_collision(pos)
            if (pin):
                return o, pin
        return False   
   
    def get_input_pos(self, pos, exclude=[]):
        pos = list(pos)
        object_list = list(self.objects.keys())
        object_list.reverse()
        for k in object_list:
            o = self.objects[k]
            if o in exclude:
                continue               
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

    def add_node(self, pos, net = False):
        o = self.canvas.cells["node"](self)
        name = "__node_%d" % (self.get_obj_id())
        self.objects[name] = o
        o.update()
        pos = "%dx%d" % (pos[0], pos[1])
        if net is False:
            net = self.add_net()
        o.parse([name, "node", pos, net.name])
        self.apply_grid(o)
        self.canvas.request_io_redraw() 
        return o     
    
    def add_net(self, net_name = False):
        if net_name is False:
            net_name = "__net_%d" % (self.get_net_id())
            
        o = self.canvas.cells["net"](self)
        self.objects[net_name] = o
        o.parse([net_name, "net"])
        
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
            
    def select_obj(self, objs):
        for o in objs:
            if o not in self.selected:
                self.selected.append(o)
                self.canvas.request_io_redraw()
                
    def deselect_obj(self, objs):
        for o in objs:
            if o in self.selected:
                self.selected.remove(o)
                self.canvas.request_io_redraw()
    
    def tglselect_obj(self, obj):
        if obj in self.selected:
            self.deselect_obj([obj])
        else:
            self.select_obj([obj])
                        
    def clear_selection(self):
        self.selected = []
        self.canvas.request_io_redraw()                
            
         
            
    def event(self, event, mode):
        
        #GET event info
        hover_object = False
        keys = pygame.key.get_pressed()
        
        if hasattr(event, "pos"):
            mouse_x = (event.pos[0] - self.pan_offset_x) / self.zoom
            mouse_y = (event.pos[1] - self.pan_offset_y) / self.zoom
            
            hover_object = self.get_object_pos([mouse_x, mouse_y])
        
        if event.type == pygame.KEYDOWN:
            if event.key == ord('a'):
                self.canvas.set_mode(MODE_ADD)           
            if event.key == ord('e'):
                self.canvas.set_mode(MODE_EDIT)  
            if event.key == ord('w') and self.canvas.mode == MODE_EDIT:
                self.canvas.set_mode(MODE_WIRE)   
            if event.key == pygame.K_ESCAPE:
                if self.canvas.mode == MODE_WIRE:
                    self.canvas.set_mode(MODE_EDIT)   
                else:
                    self.clear_selection()
                    self.canvas.set_mode(MODE_IDLE)   
        
        #PAN is woring allways
        #RIGHT DOWN => START PAN
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT:
            self.pan_x = event.pos[0]
            self.pan_y = event.pos[1]
            self.pan = True
        
        if self.pan:
            #RIGHT UP => STOP PAN
            if event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT:
                self.pan_offset_x += event.pos[0] - self.pan_x
                self.pan_offset_y += event.pos[1] - self.pan_y
                self.pan = False
            
                
            if event.type == pygame.MOUSEMOTION:
                self.pan_offset_x += event.pos[0] - self.pan_x
                self.pan_offset_y += event.pos[1] - self.pan_y     
                self.pan_x = event.pos[0]
                self.pan_y = event.pos[1]
                self.canvas.request_io_redraw()                  
            
        #ZOOM is working allways
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == WHEEL_UP:  
            if self.zoom < 1.5: 
                self.zoom += 0.1
                w = int(self.canvas.size[0] * self.zoom * 0.05)
                h = int(self.canvas.size[1] * self.zoom * 0.05)
                
                self.pan_offset_x -= w
                self.pan_offset_y -= h
                
                self.update_zoom()
                self.canvas.request_io_redraw()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == WHEEL_DOWN:   
            if self.zoom > 0.2:
                
                w = int(self.canvas.size[0] * self.zoom * 0.05)
                h = int(self.canvas.size[1] * self.zoom * 0.05)
                
                self.zoom -= 0.1
                
                self.pan_offset_x += w
                self.pan_offset_y += h    
                            
                self.update_zoom()
                self.canvas.request_io_redraw()
          
          
        if mode == MODE_IDLE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                if hover_object is not False:
                    hover_object.click()
            
        if mode == MODE_EDIT:
            #LEFT DOWN => START SELECT
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                if hover_object is False:
                    #SHIFT prevent clear selection
                    if not keys[pygame.K_LSHIFT]:
                        self.clear_selection()  
                        
                    self.canvas.set_mode(MODE_SELECT)  
                    self.select_start = [mouse_x, mouse_y]
                    self.select_rect = pygame.Rect(mouse_x, mouse_y, 0, 0)
                else:
                    if keys[pygame.K_LCTRL]:
                        self.tglselect_obj(hover_object)
                    else:
                        if hover_object not in self.selected:
                            self.clear_selection()
                            self.select_obj([hover_object])
                    
                    if hover_object in self.selected:    
                        self.possible_move = True       
         
            if event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
                if self.possible_move is True:
                    self.possible_move = False
         
            if event.type == pygame.MOUSEMOTION:
                if self.possible_move is True:
                    self.possible_move = False
                    for o in self.selected:
                        o.set_offset(mouse_x - o.rect[0], mouse_y - o.rect[1])
                        
                    self.canvas.set_mode(MODE_MOVE)
                    
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE:
                for o in self.selected:
                    o.disconnect()
                    del self.objects[o.name]
                self.clear_selection()
                                       
        if mode == MODE_SELECT:
            if event.type == pygame.MOUSEMOTION:
                w = mouse_x - self.select_start[0]
                h = mouse_y - self.select_start[1]
                self.select_rect = pygame.Rect(self.select_start[0], self.select_start[1], w, h)

            if event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
                self.canvas.request_io_redraw()
                for k in self.objects:
                    o = self.objects[k]
                    if (self.select_rect.colliderect(o.rect)):
                        self.select_obj([o])
                self.canvas.set_mode(MODE_EDIT);

        if mode == MODE_MOVE:           
            if event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
                for o in self.selected:
                    o.set_pos(mouse_x, mouse_y)
                    o.clear_offset()
                    self.apply_grid(o)
                    o.done_drag()
                
                if (len(self.selected) == 1):
                    self.clear_selection()
                    
                self.canvas.set_mode(MODE_EDIT);
        
            if event.type == pygame.MOUSEMOTION:
                for o in self.selected:
                    o.set_pos(mouse_x, mouse_y)

        if mode == MODE_WIRE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                if isinstance(hover_object, wire.Node):
                    self.new_node = self.add_node([mouse_x, mouse_y], hover_object.net)
                    self.new_node.set_offset(self.new_node.rect.w / 2, self.new_node.rect.h / 2)
                    self.new_node.add_sibling(hover_object)
                    self.new_node.set_pos(mouse_x, mouse_y)     
                else:
                    if hover_object is False: 
                        start_node = self.add_node([mouse_x, mouse_y])
                        start_node.set_offset(start_node.rect.w / 2, start_node.rect.h / 2)
                        start_node.set_pos(mouse_x, mouse_y)
                        self.apply_grid(start_node)
                        
                        self.new_node = self.add_node([mouse_x, mouse_y], start_node.net)
                        self.new_node.set_offset(self.new_node.rect.w / 2, self.new_node.rect.h / 2)
                        self.new_node.add_sibling(start_node)      
                        self.new_node.set_pos(mouse_x, mouse_y)              
                             
            if event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
                if self.new_node is not False:
                    self.new_node.set_pos(mouse_x, mouse_y)
                    self.new_node.clear_offset()
                    self.apply_grid(self.new_node)
                    
                    target = self.get_input_pos([mouse_x, mouse_y], [self.new_node])
                    print "get_input_pos", target
                    if target is not False:
                        obj, pin = target
                        obj.assign_input(pin, self.new_node.siblings[0], "Y")
                        self.delete(self.new_node.name)
                        self.new_node = False
                        return
                    
                    target = self.get_output_pos([mouse_x, mouse_y], [self.new_node])
                    print "get_output_pos", target
                    if target is not False:
                        obj, pin = target
                        self.new_node.siblings[0].assign_free_input(obj , pin)
                        self.delete(self.new_node.name)
                        self.new_node = False
                        return                    
                    
                    target = self.get_object_pos([mouse_x, mouse_y], [self.new_node])
                    print "get_object_pos", target
                    if target is not False:
                        if isinstance(target, wire.Node):
                            prev = self.new_node.siblings[0]
                            target.add_sibling(prev)
                            if prev.net is not target.net:
                                prev.net.asimilate(target.net)

                            self.delete(self.new_node.name)
                            self.new_node = False
                        return     
                    
                    target = self.get_line_pos([mouse_x, mouse_y])
                    print "get_line_pos", target
                    if target is not False:
                        obj, obj_pin, inp, inp_pin = target
                        if isinstance(inp, wire.Node):
                            inp.add_sibling(self.new_node)
                            self.new_node.net.asimilate(inp.net)
                        else:
                            self.new_node.assign_free_input(inp , inp_pin)
                            
                        if isinstance(obj, wire.Node):
                            obj.add_sibling(self.new_node)
                            self.new_node.net.asimilate(inp.net)
                        else:
                            obj.assign_input(obj_pin, self.new_node, "Y")                

                    self.new_node = False
                               
            if event.type == pygame.MOUSEMOTION:
                if self.new_node is not False:
                    self.new_node.set_pos(mouse_x, mouse_y)
        
            
#         if mode == MODE_DEL:
#             if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
#                 o = self.get_object_pos([mouse_x, mouse_y])
#                 if o:
#                     self.delete(o.name)
#                     self.canvas.request_io_redraw()
#                     self.canvas.reset_mode()
#                 else:
#                     w = self.get_line_pos([mouse_x, mouse_y])
#                     if w:
#                         o = w[0]
#                         p = w[1]
#                         o.clear_input(p)
#                         self.canvas.request_io_redraw()
#                         self.canvas.reset_mode()                        
#              
#         if mode == MODE_ADD:
#             if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
#                 fcs = self.canvas.cells.keys()[self.canvas.add_cell_index]
#                 self.add_object(fcs, [mouse_x, mouse_y])   
#             
#             if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
#                 self.canvas.inc_cell_index()        
# 
#             if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
#                 self.canvas.dec_cell_index()            
#         
#         if mode == MODE_WIRE:
#             pass
#             if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
#                 start = self.get_output_pos([mouse_x, mouse_y])
#                 if start is not False:
#                     p = self.canvas.style["d_point"]
# 
#                     self.move = self.add_object("wire", [mouse_x + 2*p, mouse_y + 2*p])
#                     self.move.assign_free_input(start[0], start[1])
# 
#                     self.move_offset = [2 * p + self.pan_offset_x, 2 * p + self.pan_offset_y]
#                 else:
#                     w = self.get_line_pos([mouse_x, mouse_y])
#                     if w:
#                         in_cell = w[0]
#                         in_pin = w[1]
#                         out_cell = w[2]
#                         out_pin = w[3]
#                         
#                         p = self.canvas.style["d_point"]
#     
#                         self.move = self.add_object("wire", [mouse_x + 2*p, mouse_y + 2*p])
#                         self.move.assign_free_input(out_cell, out_pin)
#                         in_cell.assign_input(in_pin, self.move, "Y")
#     
#                         self.move_offset = [2 * p + self.pan_offset_x, 2 * p + self.pan_offset_y]                        
#                         
#                         
# 
#             if event.type == pygame.MOUSEMOTION:
#                 if self.move is not False:
#                     self.move.set_pos(mouse_x, mouse_y)
#                     self.canvas.request_io_redraw()
# 
#             if event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
#                 if self.move is not False:
#                     end = self.get_input_pos([mouse_x, mouse_y], exclude = [self.move.name])
#                     if end is not False:
#                         obj_input = self.move.inputs["A"]
#                         end[0].assign_input(end[1], obj_input[0], obj_input[1])
#                         self.delete(self.move.name)
#                     else:
#                         self.apply_grid(self.move)
#                         self.move.done_drag()   
#                         
#                     self.move = False
#                     self.canvas.request_io_redraw()
