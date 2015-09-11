import pygame
import basic_logic
import outputs
import inputs
import module


LEFT = 1
RIGHT = 3

class Canvas():
    
    def __init__(self):
        self.size = (800, 600)
        self.screen = pygame.display.set_mode(self.size, pygame.DOUBLEBUF | pygame.RESIZABLE)
        
        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 10)        
        
        self.c_border = (0, 0, 255)
        self.c_fill = (255, 255, 255)
        self.c_text = (10, 10, 10)
        self.c_low = (200, 200, 200)
        self.c_high = (0, 255, 0)
        
        self.d_width = 60
        self.d_input = 20
        self.d_output = 20
        self.d_line = 25
        
        self.g_hor = 10
        self.g_ver= 10
        
        self.objects = []
        self.objects_ref = {}
        self.cells = {}
        
        self.add_cell("tgl", inputs.Toggle)
        self.add_cell("const", inputs.Constant)
        
        self.add_cell("and", basic_logic.And)
        self.add_cell("or", basic_logic.Or)
        self.add_cell("xor", basic_logic.Xor)
        self.add_cell("not", basic_logic.Not)
        self.add_cell("nor", basic_logic.Nor)
        self.add_cell("nand", basic_logic.Nand)
        
        self.add_cell("led", outputs.Led)
        self.add_cell("hex", outputs.HexDisplay)
        
        self.add_cell("input", module.module_input)
        self.add_cell("output", module.module_output)
        self.add_cell("module", module.module)
        
    def add_cell(self, name, cell):
        self.cells[name] = cell
        
    def write_file(self, filename):
        lines = ""
        for k in self.objects:
            o = self.objects_ref[k]
            
            name = o.name
            fcs = o.type
            pos_x = str(o.x)
            pos_y = str(o.y)
            print o.get_params()
            params = " ".join(o.get_params())
            line = name, fcs, pos_x, pos_y, params
            lines += "%s\n" % "\t".join(line)
        
        f = open(filename, "w")
        f.write(lines)
        f.close()
        
            
   
    def read_file(self, filename, owner=False):
        print "Reading file", filename
        if owner is False:
            owner = self
                
        f = open(filename, "r")
        data = f.readlines()
        f.close()
        
        params = self.create_objects(data, owner)
        self.connect_objects(params, owner)

        print self.objects
        print "done", filename
        
    def create_objects(self, data, owner):
        y = 10
        params = []
        params_ref = {}
        line_n = 0
            

        for line in data:
            if line == "":
                continue
            if line[0] == "#":
                continue
            
            arr = line.split()
            if len(arr) == 0:
                continue
            
            print "%5d: %s" % (line_n, " ".join(arr))
            line_n += 1 
            
            name = arr[0]
            fcs = arr[1]

            if (len(arr) > 2):
                pos_x = arr[2]
            else:
                pos_x = "?"
                
            if (len(arr) > 3):
                pos_y = arr[3]
            else:
                pos_y = "?"

            if pos_x == "?":
                pos_x = 10
            else:
                pos_x = int(pos_x)
            if pos_y == "?":
                pos_y = y
            else:
                pos_y = int(pos_y)
            
            
            o = False
            if fcs in self.cells:
                o = self.cells[fcs](owner, (pos_x, pos_y))
            
            if (o is not False):
                params.append(name)
                params_ref[name] = arr
                owner.objects.append(name)
                owner.objects_ref[name] = o
                o.set_name(name)
                o.set_type(fcs)
                y += o.get_rect()[3] + 10
        
        print
        return params, params_ref
   
    def find_cell_pin(self, name):
        arr = name.split(".")
        if (len(arr) == 1):
            o_name = arr[0]
            o_pin = False
        else:
            o_name, o_pin = arr
            
        o = self.objects_ref[o_name]
        if not o_pin:
            o_pin = o.outputs[0]
        
        return o, o_pin    
        
    def connect_objects(self, data, owner):
        print data
        for name in data[0]:
            arr = data[1][name]
            print arr

            o = owner.objects_ref[name]
            o.parse(arr)
        
        
        
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
#         lines = (start, (xm, y1), (xm, ym), (xm, y2), end)
        pygame.draw.lines(self.screen, color, False, lines, 2)
        
        
    def draw(self):
        for k in self.objects:
            self.objects_ref[k].draw()
        
    def tick(self):
        for k in self.objects:
            self.objects_ref[k].tick()        
        
    def reset(self):
        for k in self.objects:
            self.objects_ref[k].reset()        
        
    def get_object_pos(self, pos):
        for k in self.objects:
            o = self.objects_ref[k]
            if (o.get_rect().collidepoint(pos)):
                return o
        return False
            
        
    def events(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
            o = self.get_object_pos(event.pos)
            if o is not False:
                o.click()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHT:
            self.move = self.get_object_pos(event.pos)
            if self.move is not False:
                rect = self.move.get_rect()
                self.move_offest = [event.pos[0] - rect[0], event.pos[1] - rect[1]]
                

        if event.type == pygame.MOUSEBUTTONUP and event.button == RIGHT:
            if self.move is not False:
                x = int(round((event.pos[0] - self.move_offest[0]) / float(self.g_hor)) * self.g_hor)
                y = int(round((event.pos[1] - self.move_offest[1]) / float(self.g_ver)) * self.g_ver)
                self.move.set_pos((x, y))
            self.move = False

        if event.type == pygame.MOUSEMOTION:
            if self.move is not False:
                x = event.pos[0] - self.move_offest[0]
                y = event.pos[1] - self.move_offest[1]
                self.move.set_pos((x, y))

        if event.type == pygame.VIDEORESIZE:
            self.screen = pygame.display.set_mode(event.dict['size'], pygame.DOUBLEBUF | pygame.RESIZABLE)
            
    def loop(self):
        self.screen.fill((0, 0, 0))
        self.events()
        self.tick()
        self.draw()
        pygame.display.flip()
        
    def run(self):
        self.move = False
        self.move_offest = [0,0]
        self.running = True;
        self.reset()
        while (self.running):
            self.loop()    
    
        
canvas = Canvas()

canvas.read_file("net.txt")
canvas.run()
# canvas.write_file("net.txt")