import pygame
from controller import Controller
from collections import OrderedDict

import basic_logic
import inputs
import outputs
import module

LEFT = 1
RIGHT = 3

class Canvas():
    def __init__(self):
        self.size = (800, 600)
        self.screen = pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.HWSURFACE)
        
        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 10)
        
        self.style = {
            "c_border": (0, 0, 255),
            "c_fill": (255, 255, 255),
            "c_text": (10, 10, 10),
            "c_low": (200, 200, 200),
            "c_high": (0, 255, 0),
        
            "d_width": 60,
            "d_input": 20,
            "d_output": 20,
            "d_line": 25,
            "d_label": 20,
            "d_point": 6,
            "d_line_height": 2,
            "d_space": 10,
        
            "g_hor" : 10,
            "g_ver": 10,
        }        
        
        self.controller = Controller(self, False)
        
        self.cells = OrderedDict()
        
        self.add_cell("and", basic_logic.And)
        self.add_cell("or", basic_logic.Or)
        self.add_cell("nand", basic_logic.Nand)
        self.add_cell("nor", basic_logic.Nor)
        self.add_cell("xor", basic_logic.Xor)
        self.add_cell("not", basic_logic.Not)
        
        self.add_cell("tgl", inputs.Toggle)
        self.add_cell("const", inputs.Constant)
        
        self.add_cell("led", outputs.Led)
        self.add_cell("hex", outputs.HexDisplay)
        
        self.add_cell("module", module.module)        
        self.add_cell("input", module.minput)        
        self.add_cell("output", module.moutput)        
  
    def add_cell(self, name, cell):
        self.cells[name] = cell          
        
    def draw_text(self, text, rect):
        tmp = self.font.render(text, True, self.style["c_text"])
        rect2 = tmp.get_rect();
        rect = [rect[0] + rect[2] / 2 - rect2[2]/2, rect[1] + rect[3] / 2 - rect2[3]/2]
        
        self.screen.blit(tmp,  rect)
        
    def draw_line(self, start, end, color):
        x1 = start[0]
        y1 = start[1]
        x2 = end[0]
        y2 = end[1]
        xm = x1 + (x2 - x1) / 2
        ym = y1 + (y2 - y1) / 2
        
        lines = (start, end)
#         lines = (start, (xm, y1), (xm, ym), (xm, y2), end)
        pygame.draw.lines(self.screen, color, False, lines, self.style["d_line_height"])
        
        
    def events(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.running = False
            return
            
        if event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode(event.dict['size'], pygame.DOUBLEBUF | pygame.RESIZABLE)
            return
         
        self.controller.event(event)
            
    def loop(self):
        self.screen.fill((0, 0, 0))
        self.events()
        self.controller.tick()
        self.controller.draw()
        pygame.display.flip()
        
    def run(self):
        self.running = True;
        self.controller.reset()
        while (self.running):
            self.loop()    

filename = "net.txt"

a = Canvas()
a.controller.read_file(filename)
a.run()
a.controller.write_file(filename)