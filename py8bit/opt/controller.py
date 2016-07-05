from collections import OrderedDict
from cell import High, Low, Invisible

import wire
import cell

import pygame
import utils
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
MODE_ADD_MODULE = 8
MODE_STEP = 9
MODE_RENAME = 10

NODE_DIR_NA = 0
NODE_DIR_FROM_NODE = 1
NODE_DIR_FROM_INPUT = 2
NODE_DIR_FROM_OUTPUT = 3

LIGHT_NONE = 0
LIGHT_POINT = 1
LIGHT_LINE = 2

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
        self.new_node_direction = NODE_DIR_NA

        self.zoom = 1.0
        self.zoom_step = 0.1
             
        self.obj_id = 0
        self.net_id = 0
        
        self.highlight_mode = LIGHT_NONE
        self.highlight_pos = False
        
        self.add_index = 0
        self.add_list = ["label", "and", "or", "nand", "nor", "xor", "not", "diode", "led", "hex", "tgl", "clk", "input", "output", "memory"]
        
        self.font = pygame.font.Font(pygame.font.get_default_font(), int(self.canvas.style["d_font"] * self.zoom))
        self.label_font = pygame.font.Font(pygame.font.get_default_font(), int(self.canvas.style["d_label_font"] * self.zoom))
        
        self.need_solve_drawable = True
        self.drawable = []
        
    def highlight(self, mode, pos = False):
        self.highlight_mode = mode
        self.highlight_pos = pos
        self.canvas.request_io_redraw()
        
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
        
#         print "Writing file", filename
        line_n = 0
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
            line = "\t".join([name, fcs, params])
            lines += "%s\n" % line

#             print " %5d: %s" % (line_n, line)  
            line_n += 1
        
        f = open(filename, "w")
        f.write(lines)
        f.close() 
#         print "done", filename
        
    def read_file(self, filename):
        print "Reading file", filename
        
        try:        
            f = open(filename, "r")
            data = f.readlines()
            f.close()
            
            self.create_objects(data)
    
            print "done", filename
            return True
        except IOError:
            print "not found"
            return False
        
    def create_objects(self, data):
        params = OrderedDict()
        line_n = 0

        for line in data:
            line_n += 1 
            
            arr = line.split()
            
            print " %5d: %s" % (line_n, " ".join(arr))
            
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
                        self.net_id = max(net_id + 1, self.net_id)
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
            print name, "not found!"
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
        rect.x += self.pan_offset_x
        rect.y += self.pan_offset_y
        rect.x *= self.zoom
        rect.y *= self.zoom
        
        self.canvas.screen.blit(surface, rect)
        
    def draw_circle(self, pos, state):
        pos = list(pos)
        pos[0] += self.pan_offset_x
        pos[1] += self.pan_offset_y        
        pos = [int(x * self.zoom) for x in pos] 
        if (state):
            color = self.canvas.style["c_high"]
        else:
            color = self.canvas.style["c_low"]

        self.canvas.draw_circle(color, pos, self.zoom) 
        
    def draw_line(self, start, end, state):     
        #copy the data
        start = list(start)
        end = list(end)
        
        start[0] += self.pan_offset_x
        start[1] += self.pan_offset_y
        end[0] += self.pan_offset_x
        end[1] += self.pan_offset_y

        start =  [int(x * self.zoom) for x in start] 
        end = [int(x * self.zoom) for x in end] 

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
        
    def draw_label(self, text, rect):
        tmp = self.label_font.render(text, True, self.canvas.style["c_label"])
        rect2 = tmp.get_rect()
        rect = Rect([int(x * self.zoom) for x in rect]) 
        rect = [rect.x + rect.w / 2 - rect2.w / 2, rect.y + rect.h / 2 - rect2.h / 2]
        
        return tmp
        
    def label_font_size(self, text):
        label_font = pygame.font.Font(pygame.font.get_default_font(), self.canvas.style["d_label_font"])
        tmp = label_font.render(text, True, self.canvas.style["c_text"])
        rect2 = tmp.get_rect()

        return rect2
        
    def draw_highlight(self):
        if self.highlight_mode == LIGHT_LINE:
            start = list(self.highlight_pos[0])
            end = list(self.highlight_pos[1])
            
            width = self.canvas.style["d_line_height"]
            w = int(width * self.zoom)
            
            start[0] += self.pan_offset_x
            start[1] += self.pan_offset_y
            start = [int(x * self.zoom) for x in start] 
            
            end[0] += self.pan_offset_x
            end[1] += self.pan_offset_y
            end = [int(x * self.zoom) for x in end] 
            
            if width > 0 and w == 0:
                w = 1
            pygame.draw.line(self.canvas.screen, self.canvas.style["c_highlight"], start, end, w)        

        if self.highlight_mode == LIGHT_POINT:
            width = self.canvas.style["d_point"]
            w = int(width * self.zoom)
            
            point = list(self.highlight_pos)
            point[0] += int(self.pan_offset_x)
            point[1] += int(self.pan_offset_y)
            point = [int(x * self.zoom) for x in point] 
            
            if width > 0 and w == 0:
                w = 1
            pygame.draw.circle(self.canvas.screen, self.canvas.style["c_highlight"], point, w)        
        
    def draw_highlight_box(self, rect):
        rect = Rect(rect)
        width = self.canvas.style["d_line_height"]
        w = int(width * self.zoom)
        rect.x += self.pan_offset_x
        rect.y += self.pan_offset_y
        rect = Rect([int(x * self.zoom) for x in rect]) 
        if width > 0 and w == 0:
            w = 1
        pygame.draw.rect(self.canvas.screen, self.canvas.style["c_highlight"], rect, w)
        
    def mk_surface(self, rect):
        size = [int(rect.w * self.zoom), int(rect.h * self.zoom)]
        return pygame.Surface(size, self.canvas.surface_flags)
        
    def update_zoom(self):
        self.font = pygame.font.Font(pygame.font.get_default_font(), int(self.canvas.style["d_font"] * self.zoom))
        self.label_font = pygame.font.Font(pygame.font.get_default_font(), int(self.canvas.style["d_label_font"] * self.zoom))

        self.solve_drawable()

        for k in self.objects:
            self.objects[k].request_update_body()
              
        if self.canvas.mode == MODE_ADD:
            self.new_node.request_update_body()
            
        self.canvas.request_redraw()
        
    def request_redraw(self):
        for o in self.drawable:
            o.request_redraw()     
        
    def solve_drawable(self):
        self.need_solve_drawable = True
                
    def draw(self, mode):

        if self.need_solve_drawable:
            self.need_solve_drawable = False
            window = Rect(-self.pan_offset_x, -self.pan_offset_y, self.canvas.size[0] / self.zoom, self.canvas.size[1] / self.zoom)
            self.drawable = []
            
            for k in self.objects:
                self.objects[k].solve_drawable(window, self.drawable)      
        
        if mode == MODE_SELECT:
            self.canvas.request_redraw()
            self.canvas.request_io_redraw()
        
        for o in self.drawable:
            o.draw()
            o.draw_io()
       
        if mode == MODE_SELECT:
            self.select_rect.normalize()
            self.draw_highlight_box(self.select_rect)
        
        for o in self.selected:
            self.draw_highlight_box(o.rect)

        if mode == MODE_WIRE:            
            self.draw_highlight()
            
        if mode in [MODE_ADD, MODE_ADD_MODULE]:
            if self.new_node is not False:
                self.new_node.draw()
                self.new_node.draw_io()
        
    def tick(self):
        for k in self.objects:
            self.objects[k].tick()        
         
    def reset(self):
        for k in self.objects:
            self.objects[k].reset()     
            
    def request_update(self): pass
            
    def clear_io_cache(self):
        for o in self.drawable:
            o.clear_io_cache()              
            
    def get_object_pos(self, pos, exclude = []):
        pos = list(pos)
        
        object_list = list(self.drawable)
        object_list.reverse()
        
        for o in object_list:
            if o in exclude:
                continue               
            if (o.rect.collidepoint(pos)):
                return o
        return False        
    
    #wire form input / output
    def get_line_pos(self, pos, exclude = []):
        pos = list(pos)
        
        for o in self.drawable:
            if o in exclude:
                continue
            
            data = o.check_input_line_collision(pos)
            if (data):
                if data[2] in exclude:
                    continue
                return data
        return False   
    
    #wire form net
    def get_net_line_pos(self, pos, exclude=[]):
        pos = list(pos)
        
        for o in self.drawable:
            if isinstance(o, wire.Node):
                if o in exclude:
                    continue
                
                data = o.check_net_line_collision(pos)
                if (data):
                    if data[1] in exclude:
                        continue
                    
                    return data
        return False  
    
    def get_output_pos(self, pos, exclude=[]):
        pos = list(pos)

        for o in self.drawable:
            if o in exclude:
                continue            
            
            pin = o.check_output_collision(pos)
            if (pin):
                return o, pin
        return False   
   
    def get_input_pos(self, pos, exclude=[]):
        pos = list(pos)
        
        for o in self.drawable:
            if o in exclude:
                continue               
            pin = o.check_input_collision(pos)
            if (pin):
                return o, pin
        return False     
            
        
    def add_object(self, fcs, pos, params = []):
        o = self.canvas.cells[fcs](self)
        name = "__%s_%d" % (fcs, self.get_obj_id())
        self.objects[name] = o
        o.update()
        o.middle_offset()
        pos = "%dx%d" % (pos[0], pos[1])
        o.parse([name, fcs, pos] + params)
        self.request_redraw()
        self.solve_drawable()
        return o     

    def add_node(self, pos, net = False):
        o = self.canvas.cells["node"](self)
        name = "__node_%d" % (self.get_obj_id())
        self.objects[name] = o
        o.update()
        o.middle_offset()
        pos = "%dx%d" % (pos[0], pos[1])
        if net is False:
            net = self.add_net()
        o.parse([name, "node", pos, net.name])
        self.request_redraw()
        self.solve_drawable()
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
        obj.clear_offset()
        obj.update_io_xy()
        
    def delete(self, name):
        if name in self.objects:
            self.objects[name].disconnect()
            del self.objects[name]
            self.canvas.request_redraw()
            self.solve_drawable()
            
    def select_obj(self, objs):
        for o in objs:
            if o not in self.selected and not isinstance(o, Invisible):
                self.selected.append(o)
                #self.canvas.request_io_redraw()
                
    def deselect_obj(self, objs):
        for o in objs:
            if o in self.selected:
                self.selected.remove(o)
                self.canvas.request_redraw()
    
    def tglselect_obj(self, obj):
        if obj in self.selected:
            self.deselect_obj([obj])
        else:
            self.select_obj([obj])
                        
    def clear_selection(self):
        self.selected = []
        #self.canvas.request_io_redraw()                
            
    def rename_obj(self, obj, new_name):
        if new_name in self.objects:
            return False
        
        del self.objects[obj.name]
        obj.name = new_name
        self.objects[new_name] = obj
        obj.update()
        
        return True
            
    def event(self, event, mode):
        
        #GET event info
        hover_object = False
        keys = pygame.key.get_pressed()
        
        if hasattr(event, "pos"):
            mouse_x = (event.pos[0] / self.zoom) - self.pan_offset_x
            mouse_y = (event.pos[1] / self.zoom) - self.pan_offset_y
            
            hover_object = self.get_object_pos([mouse_x, mouse_y])
            
            if keys[pygame.K_LCTRL]:
                g_hor = self.canvas.style["g_hor"]
                g_ver = self.canvas.style["g_ver"]        
                mouse_x = int(round(mouse_x / float(g_hor)) * g_hor)
                mouse_y = int(round(mouse_y / float(g_ver)) * g_ver)
        
        if event.type == pygame.KEYDOWN:
            if event.key == ord('a') and self.canvas.mode == MODE_EDIT:
                fcs = self.add_list[self.add_index]
                pos = "%dx%d" % (0, 0)
                name = "_%s_" % fcs
                self.new_node = self.canvas.cells[fcs](self)
                self.new_node.update()
                self.new_node.middle_offset()
                self.new_node.parse([name, fcs, pos])
                self.canvas.set_mode(MODE_ADD)        
                   
            if event.key == ord('m') and self.canvas.mode == MODE_EDIT:
                self.canvas.set_mode(MODE_ADD_MODULE)    
                       
            if event.key == ord('e') and self.canvas.mode in [MODE_IDLE, MODE_WIRE, MODE_RENAME]:
                self.highlight(LIGHT_NONE)
                self.canvas.set_mode(MODE_EDIT)  
                
            if event.key == ord('d') and self.canvas.mode == MODE_IDLE:
                self.canvas.set_mode(MODE_STEP)    
                              
            if event.key == ord('w') and self.canvas.mode == MODE_EDIT:
                self.canvas.set_mode(MODE_WIRE)  
                 
            if event.key == ord('r') and self.canvas.mode == MODE_EDIT:
                self.canvas.set_mode(MODE_RENAME)                   
                 
            if event.key == pygame.K_SPACE and self.canvas.mode == MODE_STEP:
                self.tick()
                                 
            if event.key == pygame.K_ESCAPE:
                self.canvas.request_io_redraw()
                if self.canvas.mode == MODE_STEP:                                   
                    self.canvas.set_mode(MODE_IDLE)                   
                
                if self.canvas.mode == MODE_EDIT:                                   
                    self.clear_selection()
                    self.canvas.set_mode(MODE_IDLE)   
                    
                if self.canvas.mode == MODE_WIRE:
                    self.canvas.set_mode(MODE_EDIT)   
                    self.highlight(LIGHT_NONE)

                if self.canvas.mode == MODE_ADD:
                    self.canvas.set_mode(MODE_EDIT)   
                    self.new_node = False

                if self.canvas.mode == MODE_ADD_MODULE:
                    self.canvas.set_mode(MODE_EDIT)   
                    self.new_node = False
                    
                if self.canvas.mode == MODE_RENAME:                                   
                    self.canvas.set_mode(MODE_EDIT)          
        
        #PAN is woring allways
        #RIGHT DOWN => START PAN
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == MID:
            self.pan_x = event.pos[0] / self.zoom
            self.pan_y = event.pos[1] / self.zoom
            self.pan = True
            self.mode_before = mode
            self.canvas.set_mode(MODE_PAN)
        
        if self.pan:
            #RIGHT UP => STOP PAN
            if event.type == pygame.MOUSEBUTTONUP and event.button == MID:
                self.pan_offset_x += event.pos[0] / self.zoom - self.pan_x
                self.pan_offset_y += event.pos[1] / self.zoom - self.pan_y
                self.solve_drawable()
                self.canvas.request_redraw()
                self.pan = False
                self.canvas.set_mode(self.mode_before)
            
            if event.type == pygame.MOUSEMOTION:
                self.pan_offset_x += event.pos[0] / self.zoom - self.pan_x
                self.pan_offset_y += event.pos[1] / self.zoom - self.pan_y     
                self.pan_x = event.pos[0] / self.zoom
                self.pan_y = event.pos[1] / self.zoom
                
                self.solve_drawable()
                self.canvas.request_redraw()
      
            
        #ZOOM is working allways
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == WHEEL_UP:  
            if self.zoom < 1.5:
                             
                self.pan_offset_x -= mouse_x + self.pan_offset_x - event.pos[0] / self.zoom
                self.pan_offset_y -= mouse_y + self.pan_offset_y - event.pos[1] / self.zoom
                self.zoom += self.zoom_step                 

                self.update_zoom()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == WHEEL_DOWN:   
            if self.zoom > 0.2:
                
                self.zoom -= self.zoom_step
                
                           
                self.update_zoom()
          
        if mode == MODE_IDLE or mode == MODE_STEP:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                if hover_object is not False:
                    hover_object.click()
        
        if mode == MODE_RENAME:
            #LEFT DOWN => RENAME
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                if hover_object is not False:
                    if isinstance(hover_object, cell.Label):
                        label = utils.gui_textedit("Change the label", hover_object.label)
                        if len(label) == 0:
                            utils.gui_alert("Error", "Labels can't be empty")
                        else:
                            hover_object.label = label
                            hover_object.update()
                            self.canvas.set_mode(MODE_EDIT)
                    else:
                        if isinstance(hover_object, wire.Node):
                            obj = hover_object.net
                        else:
                            obj = hover_object
                        
                        old_name = obj.name    
                        name = utils.gui_textedit("Rename the object", obj.name)
                        if old_name == name:
                            return
                        
                        if len(name) == 0:
                            utils.gui_alert("Error", "Name can't be empty")
                            return
                        
                        if not self.rename_obj(obj, name):
                            utils.gui_alert("Error", "Unable to rename object")
                        else:
                            self.canvas.set_mode(MODE_EDIT)    
                        
              
            
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
                    if keys[pygame.K_LSHIFT]:
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
                    self.delete(o.name)
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
                self.canvas.request_redraw()
                for o in self.selected:
                    o.set_pos(mouse_x, mouse_y)
                    self.apply_grid(o)
                
                if (len(self.selected) == 1):
                    self.clear_selection()
                    
                self.canvas.set_mode(MODE_EDIT);
        
            if event.type == pygame.MOUSEMOTION:
                self.canvas.request_redraw()
                for o in self.selected:
                    o.set_pos(mouse_x, mouse_y)

        if mode == MODE_WIRE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                print 
                print "<<"
                
                print "get_object_pos", hover_object
                if isinstance(hover_object, wire.Node):
                    self.new_node = self.add_node([mouse_x, mouse_y], hover_object.net)
                    self.new_node.add_sibling(hover_object)

                    self.new_node_direction = NODE_DIR_FROM_NODE
                    self.solve_drawable()
                    return                
                
                target = self.get_input_pos([mouse_x, mouse_y])
                print "get_input_pos", target
                if target is not False:
                    obj, pin = target
                    self.new_node = self.add_node([mouse_x, mouse_y])
                    obj.assign_input(pin, self.new_node, "Y")
                    self.new_node_direction = NODE_DIR_FROM_INPUT
                    self.solve_drawable()
                    return
                
                target = self.get_output_pos([mouse_x, mouse_y])
                print "get_output_pos", target
                if target is not False:
                    obj, pin = target
                    self.new_node = self.add_node([mouse_x, mouse_y])
                    self.new_node.assign_free_input(obj, pin)
                    self.new_node_direction = NODE_DIR_FROM_OUTPUT
                    self.solve_drawable()
                    return                   
                
                target = self.get_line_pos([mouse_x, mouse_y])
                print "get_line_pos", target
                if target is not False:
                    obj, obj_pin, inp, inp_pin = target
                    start_node = self.add_node([mouse_x, mouse_y])
                    self.apply_grid(start_node)
                    
                    if isinstance(inp, wire.Node):
                        inp.add_sibling(start_node)
                        start_node.net.remove_node(self.new_node)
                        self.delete(start_node.net.name)
                        inp.net.add_node(start_node)
                    obj.assign_input(obj_pin, start_node, "Y")
                        
                    if isinstance(obj, wire.Node):
                        obj.add_sibling(start_node)
                        start_node.net.remove_node(start_node)
                        self.delete(start_node.net.name)
                        obj.net.add_node(start_node)
                    start_node.assign_free_input(inp, inp_pin)        

                    self.new_node = self.add_node([mouse_x, mouse_y], start_node.net)
                    self.new_node.add_sibling(start_node)      
                    
                    self.new_node_direction = NODE_DIR_FROM_NODE
                    self.solve_drawable()
                    return                   
                
                target = self.get_net_line_pos([mouse_x, mouse_y])
                print "get_net_line_pos", target
                if target is not False:
                    node1, node2, net = target
                    start_node = self.add_node([mouse_x, mouse_y], net)
                    self.apply_grid(start_node)                        
                    node1.remove_sibling(node2)
                    node1.add_sibling(start_node)
                    node2.remove_sibling(node1)
                    node2.add_sibling(start_node)
                    
                    self.new_node = self.add_node([mouse_x, mouse_y], start_node.net)
                    self.new_node.add_sibling(start_node)      
                    
                    self.new_node_direction = NODE_DIR_FROM_NODE
                    self.solve_drawable()
                    return     
  
                else:
                    if hover_object is False: 
                        start_node = self.add_node([mouse_x, mouse_y])
                        self.apply_grid(start_node)
                        
                        self.new_node = self.add_node([mouse_x, mouse_y], start_node.net)
                        self.new_node.add_sibling(start_node)      
                        self.new_node_direction = NODE_DIR_FROM_NODE
                        self.solve_drawable()
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == LEFT:
                if self.new_node is not False:
                    self.new_node.set_pos(mouse_x, mouse_y)
                    self.apply_grid(self.new_node)

                    print 
                    print ">>"

                    target = self.get_object_pos([mouse_x, mouse_y], [self.new_node])
                    print "get_object_pos", target
                    if target is not False:
                        if isinstance(target, wire.Node):
                            #FROM_INPUT / FROM_OUTPUT will be handeled lower
                            if self.new_node_direction == NODE_DIR_FROM_NODE:
                                prev = self.new_node.siblings[0]
                                target.add_sibling(prev)
                                prev.net.asimilate(target.net)

                                self.delete(self.new_node.name)
                                self.new_node = False
                                self.solve_drawable()
                                return
                    
                    target = self.get_input_pos([mouse_x, mouse_y], [self.new_node])
                    print "get_input_pos", target
                    if target is not False and self.new_node_direction is not NODE_DIR_FROM_INPUT:
                        obj, pin = target
                        if self.new_node_direction == NODE_DIR_FROM_NODE:
                            obj.assign_input(pin, self.new_node.siblings[0], "Y")
                        if self.new_node_direction == NODE_DIR_FROM_OUTPUT:
                            key = self.new_node.inputs.keys()[0]
                            inp, inp_pin = self.new_node.inputs[key]
                            obj.assign_input(pin, inp, inp_pin)
                        
                        self.delete(self.new_node.name)
                        self.new_node = False
                        self.solve_drawable()
                        return
                    
                    target = self.get_output_pos([mouse_x, mouse_y], [self.new_node])
                    print "get_output_pos", target
                    if target is not False and self.new_node_direction is not NODE_DIR_FROM_OUTPUT:
                        obj, pin = target
                        if self.new_node_direction == NODE_DIR_FROM_NODE:
                            self.new_node.siblings[0].assign_free_input(obj , pin)
                        if self.new_node_direction == NODE_DIR_FROM_INPUT:
                            orig_obj, orig_pin = self.find_output(self.new_node, "Y")
                            orig_obj.assign_input(orig_pin, obj, pin)
                                
                        self.delete(self.new_node.name)
                        self.new_node = False
                        self.solve_drawable()
                        return                    
                    
                    target = self.get_line_pos([mouse_x, mouse_y], [self.new_node])
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
                            obj.clear_input(obj_pin)
                            self.new_node.net.asimilate(obj.net)
                        else:
                            obj.assign_input(obj_pin, self.new_node, "Y")        
                            
                        self.new_node = False
                        self.solve_drawable()
                        return        

                    target = self.get_net_line_pos([mouse_x, mouse_y], [self.new_node])
                    print "get_net_line_pos", target
                    if target is not False:
                        node1, node2, net = target
                        node1.remove_sibling(node2)
                        node1.add_sibling(self.new_node)
                        node2.remove_sibling(node1)
                        node2.add_sibling(self.new_node)
                        self.new_node.net.asimilate(net)
                        self.new_node = False
                        self.solve_drawable()
                        return        

                    self.new_node = False
                    self.canvas.request_redraw()
                               
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT:
                if self.new_node is not False:
                    self.delete(self.new_node.name)
                    self.new_node = False
                else:
                    #delete node or split siblings or net
                    if isinstance(hover_object, wire.Node):
                        siblings = hover_object.net.list_node_sibling(hover_object)
                        if len(siblings) > 0:
                            successor = siblings[0]
                            
                            for node in siblings:
                                successor.add_sibling(node)
                                
                            for k in hover_object.inputs:
                                print "hover_object.input", k, hover_object, hover_object.inputs
                                obj, pin = hover_object.inputs[k]
                                successor.assign_free_input(obj, pin)
                                
                            target = self.find_output(hover_object, "Y")
                            while target is not False:
                                obj, pin = target
                                obj.assign_input(pin, successor, "Y")
                                target = self.find_output(hover_object, "Y")
                        
                        self.delete(hover_object.name)
                        self.highlight(LIGHT_NONE)
                        self.solve_drawable()
                        return
                    
                    target = self.get_line_pos([mouse_x, mouse_y])
                    print "get_line_pos", target
                    if target is not False:
                        obj, obj_pin, inp, inp_pin = target
                        obj.clear_input(obj_pin)
                        self.highlight(LIGHT_NONE)
                        self.solve_drawable()
                        self.canvas.request_redraw()
                        return                  
                    
                    target = self.get_net_line_pos([mouse_x, mouse_y], [self.new_node])
                    print "get_net_line_pos", target
                    if target is not False:
                        node1, node2, net = target
                        node1.remove_sibling(node2)
                        node2.remove_sibling(node1)
                        net.rebuild()
                        self.canvas.request_redraw()
                        self.highlight(LIGHT_NONE)
                        self.solve_drawable()
                        return     

            if event.type == pygame.MOUSEMOTION:
                if self.new_node is not False:
                    self.new_node.set_pos(mouse_x, mouse_y)
                    self.canvas.request_redraw()

                target = self.get_object_pos([mouse_x, mouse_y], [self.new_node])
#                 print "get_object_pos", target
                if target is not False:
                    if isinstance(target, wire.Node):
                        self.highlight(LIGHT_POINT, target.output_xy["Y"]);
                        return
                
                target = self.get_input_pos([mouse_x, mouse_y], [self.new_node])
#                 print "get_input_pos", target
                if target is not False:
                    obj, pin = target
                    pos = obj.input_xy[pin]
                    self.highlight(LIGHT_POINT, pos);
                    return
                
                target = self.get_output_pos([mouse_x, mouse_y], [self.new_node])
#                 print "get_output_pos", target
                if target is not False:
                    obj, pin = target
                    pos = obj.output_xy[pin]
                    self.highlight(LIGHT_POINT, pos);
                    return                    
                
                target = self.get_line_pos([mouse_x, mouse_y], [self.new_node])
#                 print "get_line_pos", target
                if target is not False:
                    obj, obj_pin, inp, inp_pin = target
                    
                    if isinstance(obj, wire.Node):
                        start = obj.output_xy["Y"]
                    else:
                        start = obj.input_xy[obj_pin]
                        
                    if isinstance(inp, wire.Node):
                        end = inp.output_xy["Y"]
                    else:                            
                        end = inp.output_xy[inp_pin]
                    
                    self.highlight(LIGHT_LINE, [start, end])
                    return        

                target = self.get_net_line_pos([mouse_x, mouse_y], [self.new_node])
#                 print "get_net_line_pos", target
                if target is not False:
                    node1, node2, net = target
                    start = node1.output_xy["Y"]
                    end = node2.output_xy["Y"]
                    self.highlight(LIGHT_LINE, [start, end])
                    return        

                self.highlight(LIGHT_NONE)
                
        if mode == MODE_ADD:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT:
                self.add_index = (self.add_index + 1) % len(self.add_list)
                fcs = self.add_list[self.add_index]
                pos = "%dx%d" % (mouse_x, mouse_y)
                name = "_%s_" % fcs
                self.new_node = self.canvas.cells[fcs](self)
                self.new_node.update()
                self.new_node.middle_offset()
                self.new_node.parse([name, fcs, pos])
                self.new_node.drawable = True
                self.canvas.request_redraw()
                                
            if event.type == pygame.MOUSEMOTION:
                if self.new_node is not False:
                    self.new_node.set_pos(mouse_x, mouse_y)
                    self.new_node.clear_io_cache()
                    self.canvas.request_redraw()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                o = self.add_object(self.add_list[self.add_index], [mouse_x, mouse_y])
                self.apply_grid(o)
                
        if mode == MODE_ADD_MODULE:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT:
                fcs = "module"
                pos = "%dx%d" % (mouse_x, mouse_y)
                name = "_%s_" % fcs
                self.new_node = self.canvas.cells[fcs](self)
                self.new_node.update()
                self.new_node.middle_offset()
                self.new_node.parse([name, fcs, pos])
                self.new_node_filename = self.new_node.filename
                self.new_node.drawable = True
                self.canvas.request_redraw()
            
            if event.type == pygame.MOUSEMOTION:
                if self.new_node is not False:
                    self.new_node.set_pos(mouse_x, mouse_y)
                    self.new_node.clear_io_cache()
                    self.canvas.request_redraw()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                o = self.add_object("module", [mouse_x, mouse_y], [self.new_node_filename])
                self.apply_grid(o)                
                
                