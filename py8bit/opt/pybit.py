import pygame
import cProfile
from controller import Controller
from collections import OrderedDict

import os

import basic_logic
import outputs
import module
import cell
import inputs
import wire


from controller import MODE_IDLE, MODE_MOVE, MODE_ADD, MODE_DEL, MODE_WIRE, MODE_SELECT, MODE_EDIT
from utils import file_opendialog

class Canvas():
    def __init__(self):
        self.size = (800, 600)
        self.screen_flags = pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.HWSURFACE
        self.surface_flags = pygame.HWSURFACE
        
        self.update_surfaces()
        
        pygame.font.init()
        self.status_font = pygame.font.Font(pygame.font.get_default_font(), 20)
        
        self.style = {
            "c_border": (0, 0, 255),
            "c_fill": (255, 255, 255),
            "c_text": (10, 10, 10),
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
            
            "d_line_col": 10,
            "d_wire_col": 20,
        
            "g_hor" : 10,
            "g_ver": 10,
        }        
        
        self.controller = Controller(self, False)
        
        self.cells = OrderedDict()
        
        self.add_cell("net", wire.Net)
        self.add_cell("node", wire.Node)
        
        self.add_cell("and", basic_logic.And)
        self.add_cell("or", basic_logic.Or)
        self.add_cell("nand", basic_logic.Nand)
        self.add_cell("nor", basic_logic.Nor)
        self.add_cell("xor", basic_logic.Xor)
        self.add_cell("not", basic_logic.Not)
        
        self.add_cell("led", outputs.Led)
        self.add_cell("hex", outputs.HexDisplay)
 
        self.add_cell("tgl", inputs.Toggle)        
        
        self.add_cell("module", module.module)        
        self.add_cell("input", module.minput)        
        self.add_cell("output", module.moutput)    
        
        self.mode = MODE_IDLE
        self.add_cell_index = 0
          
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
        self.surface_io = pygame.Surface(self.size, self.surface_flags)
        self.surface_io.set_colorkey((0, 0, 0))
  
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
        
        pygame.draw.lines(self.surface_io, color, False, lines, w)
        
    def draw_circle(self, color, pos, zoom):
        pygame.draw.circle(self.surface_io, color, pos, int(zoom * self.style["d_point"]))
    
   
    def draw_status(self, text):
        tmp = self.status_font.render(text, True, self.style["c_status"])
        rect2 = tmp.get_rect();
        rect = [0, self.size[1] - rect2.h]
        
        self.screen.blit(tmp,  rect)        
        
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
                
            if event.type == pygame.VIDEORESIZE:
                self.size = event.dict['size']
                self.update_surfaces()
                self.request_io_redraw()
                return
             
            self.controller.event(event, self.mode)
        
    def reset_mode(self):
        self.mode = MODE_IDLE

    def set_mode(self, mode):
        self.mode = mode
        
    def request_io_redraw(self):
        self.surface_io.fill((0, 0, 0))
        self.controller.clear_io_cache()

    def loop(self):
        self.screen.fill((0, 0, 0))
        self.events()
        for i in range(20):
            self.controller.tick()
            
        self.controller.draw(self.mode)
        self.screen.blit(self.surface_io, [0, 0])
        
        if self.mode == MODE_MOVE:
            self.draw_status("move")
        if self.mode == MODE_ADD:
            self.draw_status("add %s" % self.cells.keys()[self.add_cell_index])
        if self.mode == MODE_EDIT:
            self.draw_status("edit")
        if self.mode == MODE_WIRE:
            self.draw_status("wire")    
        if self.mode == MODE_SELECT:
            self.draw_status("select")                        
        
        pygame.display.flip()
        
    def run(self):
        self.running = True;
        self.controller.reset()
        while (self.running):
            self.loop()    


filename = file_opendialog(os.getcwd())

profile = False

a = Canvas()
a.controller.read_file(filename)
if profile:
    cProfile.run("a.run()", sort="tottime")
else:
    a.run()
a.controller.write_file(filename)