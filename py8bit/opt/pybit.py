import pygame
import cProfile
from controller import Controller, MODE_ADD_MODULE, MODE_STEP, MODE_RENAME
from collections import OrderedDict

import basic_logic
import outputs
import module
import cell
import inputs
import wire
import memory


from controller import MODE_IDLE, MODE_MOVE, MODE_ADD, MODE_WIRE, MODE_SELECT, MODE_EDIT, MODE_PAN
from utils import file_opendialog
from pygame.rect import Rect

class Canvas():
    def __init__(self):
        self.size = (800 , 600)
        self.screen_flags = pygame.RESIZABLE
        self.surface_flags = 0
        
        pygame.font.init()
        self.status_font = pygame.font.Font(pygame.font.get_default_font(), 20)
        
        self.style = {
            "c_border": (0, 0, 255),
            "c_fill": (255, 255, 255),
            "c_text": (10, 10, 10),
            "c_label": (173, 216, 230),
            "c_status": (255, 255, 255),
            "c_low": (200, 200, 200),
            "c_high": (0, 255, 0),
            "c_highlight": (0, 255, 255),
        
            "d_width": 60,
            "d_input": 20,
            "d_output": 20,
            "d_line": 20,
            "d_label": 20,
            "d_point": 4,
            "d_line_height": 2,
            "d_space": 10,
            "d_font": 10,
            "d_label_font": 40,
            
            "d_line_col": 5,
            "d_wire_col": 5,
        
            "g_hor" : 10,
            "g_ver": 10,
        }        
        
        self.controller = Controller(self, False)

        self.update_surfaces()
        self.need_redraw = True
        self.need_io_redraw = True
        
        self.cells = OrderedDict()

        self.add_cell("label", cell.Label)
        
        self.add_cell("net", wire.Net)
        self.add_cell("node", wire.Node)
        
        self.add_cell("and", basic_logic.And)
        self.add_cell("or", basic_logic.Or)
        self.add_cell("nand", basic_logic.Nand)
        self.add_cell("nor", basic_logic.Nor)
        self.add_cell("xor", basic_logic.Xor)
        self.add_cell("not", basic_logic.Not)
        self.add_cell("diode", basic_logic.Diode)
        
        self.add_cell("led", outputs.Led)
        self.add_cell("hex", outputs.HexDisplay)
 
        self.add_cell("tgl", inputs.Toggle)        
        self.add_cell("clk", inputs.Clock)        
        
        self.add_cell("module", module.module)        
        self.add_cell("input", module.minput)        
        self.add_cell("output", module.moutput)    
        
        self.add_cell("memory", memory.Memory)    
        
        self.mode = MODE_IDLE
        
        self.draw_clock = pygame.time.Clock()
        
        self.fps = 0

    def inc_cell_index(self):
        self.add_cell_index = (self.add_cell_index + 1) % len(self.cells)

    def dec_cell_index(self):
        if self.add_cell_index == 0:
            self.add_cell_index = len(self.cells) - 1
        else:
            self.add_cell_index = self.add_cell_index - 1
           
    def update_surfaces(self):
        self.screen = pygame.display.set_mode(self.size, self.screen_flags)
        self.rect = self.screen.get_rect()
        self.controller.solve_drawable()
  
    def add_cell(self, name, cell):
        self.cells[name] = cell          
        
    def draw_text(self, text, rect):
        tmp = self.font.render(text, True, self.style["c_text"])
        rect2 = tmp.get_rect();
        rect = [rect[0] + rect[2] / 2 - rect2[2]/2, rect[1] + rect[3] / 2 - rect2[3]/2]
        
        self.screen.blit(tmp,  rect)
        
    def draw_line(self, start, end, color, zoom):
        lines = (start, end)
        w = max(int(zoom * self.style["d_line_height"]), 1)
        
        pygame.draw.lines(self.screen, color, False, lines, w)
        
    def draw_circle(self, color, pos, zoom):
        pygame.draw.circle(self.screen, color, pos, int(zoom * self.style["d_point"]))
    
   
    def draw_status(self, text):
        text = "[%03d] %s" % (self.fps, text)
        tmp = self.status_font.render(text, True, self.style["c_status"])
        rect2 = tmp.get_rect();
        rect = Rect(0, self.size[1] - rect2.h, rect2.w, rect2.h)
        
        pygame.draw.rect(self.screen, (0, 0, 0), rect)
        self.screen.blit(tmp,  rect)        
        
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
                
            if event.type == pygame.VIDEORESIZE:
                self.size = event.dict['size']
                self.update_surfaces()
                self.request_redraw()
                return
             
            self.controller.event(event, self.mode)
        
    def reset_mode(self):
        self.set_mode(MODE_IDLE)

    def set_mode(self, mode):
        self.mode = mode
        self.request_redraw()
        
    def request_io_redraw(self):
        self.need_io_redraw = True

    def request_redraw(self):
        self.need_redraw = True

    def loop(self):
        self.events()
        
        if self.mode is MODE_IDLE:
            self.controller.tick()
        
        if self.need_redraw:
            self.screen.fill((0, 0, 0))
            self.controller.request_redraw()
            self.need_redraw = False
            self.need_io_redraw = True
            
        if self.need_io_redraw:
            self.controller.clear_io_cache()
            self.need_io_redraw = False
            
        self.controller.draw(self.mode)
        
        if self.mode is MODE_IDLE:
            self.draw_status("run")
        if self.mode == MODE_MOVE:
            self.draw_status("move")
        if self.mode == MODE_ADD:
            self.draw_status("add")
        if self.mode == MODE_EDIT:
            self.draw_status("edit")
        if self.mode == MODE_WIRE:
            self.draw_status("wire")    
        if self.mode == MODE_SELECT:
            self.draw_status("select")  
        if self.mode == MODE_ADD_MODULE:
            self.draw_status("add module")     
        if self.mode == MODE_STEP:
            self.draw_status("step")   
        if self.mode == MODE_RENAME:
            self.draw_status("rename") 
        if self.mode == MODE_PAN:
            self.draw_status("pan") 
                                    
        pygame.display.update()
        
    def run(self):
        self.running = True;
        self.controller.reset()
        
        while (self.running):
            delta = self.draw_clock.tick()
            self.loop()    
            if delta is not 0:
                self.fps = 1000 / delta

profile = False
filename = file_opendialog()


if filename is not False:
    a = Canvas()
    a.controller.read_file(filename)
    if profile:
        res = cProfile.run("a.run()", sort="tottime")
    else:
        a.run()
    
    a.controller.write_file(filename)
else:
    print "No file"