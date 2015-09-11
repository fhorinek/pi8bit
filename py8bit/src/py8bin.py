import pygame
from cell import Cell
import basic_logic
import outputs

LEFT = 1
RIGHT = 3

class Canvas():
    
    def __init__(self):
        self.size = (800, 600)
        self.screen = pygame.display.set_mode(self.size, pygame.DOUBLEBUF)
        
        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 10)        
        
        self.c_border = (0, 0, 255)
        self.c_fill = (255, 255, 255)
        self.c_text = (10, 10, 10)
        self.c_low = (200, 200, 200)
        self.c_high = (0, 255, 0)
        
        self.d_width = 75
        self.d_input = 20
        self.d_output = 20
        self.d_line = 25
        
        self.objects = []
        
        c1 = basic_logic.Toggle(self, (10, 10), 0)
        self.objects.append(c1)
        c2 = basic_logic.Toggle(self, (10, 50), 1)
        self.objects.append(c2)
         
        cand = basic_logic.And(self, (130, 10))
        cand.set_input("A", c1, "Y")
        cand.set_input("B", c2, "Y")
        self.objects.append(cand)
         
        cnot = basic_logic.Not(self, (260,10))
        cnot.set_input("A", cand, "Y")
        self.objects.append(cnot)
         
        disp = outputs.HexDisplay(self, (130, 80))
        for i in range(8):
            tmp = basic_logic.Toggle(self, (10, 80 + i * 30), 0)
            disp.set_input("A%d" % i, tmp, "Y")
            self.objects.append(tmp)
        self.objects.append(disp)

        tgl1 = basic_logic.Toggle(self, (10, 320), 0)        
        tgl2 = basic_logic.Toggle(self, (10, 400), 0)        
        cnand1 = basic_logic.Nor(self, (130, 320))
        cnand2 = basic_logic.Nor(self, (130, 400))
         
        cnand1.set_input("A", tgl1, "Y")
        cnand1.set_input("B", cnand2, "Y")
        cnand2.set_input("A", tgl2, "Y")
        cnand2.set_input("B", cnand1, "Y")
         
        self.objects.append(tgl1)
        self.objects.append(tgl2)
        self.objects.append(cnand1)
        self.objects.append(cnand2)
        
        cnot = basic_logic.Not(self, (20, 450))
        cnot.set_input("A", cnot, "Y")
        self.objects.append(cnot)
        
        
    def draw_text(self, text, rect):
        tmp = self.font.render(text, True, self.c_text)
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
#        lines = (start, (xm, y1), (xm, ym), (xm, y2), end)
        pygame.draw.lines(self.screen, color, False, lines, 2)
        
        
    def draw(self):
        for o in self.objects:
            o.draw()
        
    def reset(self):
        for o in self.objects:
            o.reset()        
        
    def get_object_pos(self, pos):
        for o in self.objects:
            if (o.get_rect().collidepoint(pos)):
                return o
        return False
            
        
    def events(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
            o = self.get_object_pos(event.pos)
            if (o is not False):
                o.click()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT:
            self.move = self.get_object_pos(event.pos)
            if (self.move):
                rect = self.move.get_rect()
                self.move_offest = [event.pos[0] - rect[0], event.pos[1] - rect[1]]
                

        if event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT:
            self.move = False

        if event.type == pygame.MOUSEMOTION:
            if (self.move):
                x = event.pos[0] - self.move_offest[0]
                y = event.pos[1] - self.move_offest[1]
                self.move.set_pos((x, y))


            
    def loop(self):
        self.screen.fill((0, 0, 0))
        self.events()
        self.draw()
        self.reset()
        pygame.display.flip()
        
    def run(self):
        self.move = False
        self.move_offest = [0,0]
        self.running = True;
        while (self.running):
            self.loop()    
    
        
canvas = Canvas()
canvas.run()