import pygame
import cProfile
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
        self.screen_flags = pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.HWSURFACE
        self.surface_flags = pygame.HWSURFACE
        
        self.update_surfaces()
        
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
            "d_line": 20,
            "d_label": 20,
            "d_point": 4,
            "d_line_height": 2,
            "d_space": 10,
            "d_line_col": 4,
        
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
  
    def update_surfaces(self):
        self.screen = pygame.display.set_mode(self.size, self.screen_flags)
        self.surface_io = pygame.Surface(self.size, self.surface_flags)
        self.surface_io.set_colorkey((0, 0, 0))
  
  
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
        pygame.draw.lines(self.surface_io, color, False, lines, self.style["d_line_height"])
        
    def draw_circle(self, color, pos):
        pygame.draw.circle(self.surface_io, color, pos, self.style["d_point"])
        
        
    def events(self):
        for event in pygame.event.get():
#             event = pygame.event.poll()
            if event.type == pygame.QUIT:
                self.running = False
                return
                
            if event.type == pygame.VIDEORESIZE:
                self.size = event.dict['size']
                self.update_surfaces()
                self.request_io_redraw()
                return
             
            self.controller.event(event)
        
    def request_io_redraw(self):
        self.surface_io.fill((0, 0, 0))
        self.controller.clear_io_cache()

    def loop(self):
        self.screen.fill((0, 0, 0))
        self.events()
        self.controller.tick()
        self.controller.draw()
        self.screen.blit(self.surface_io, [0, 0])
        pygame.display.flip()
        
    def run(self):
        self.running = True;
        self.controller.reset()
        while (self.running):
            self.loop()    

filename = "net.txt"
filename = "inc/test.txt"
# filename = "inc/full_adder.txt"

profile = True

a = Canvas()
a.controller.read_file(filename)
if profile:
    cProfile.run("a.run()", sort="tottime")
else:
    a.run()
a.controller.write_file(filename)