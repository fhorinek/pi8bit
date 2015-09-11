import cell
from wx.lib.agw.aui.aui_constants import pin_bits

class module(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.objects = []
        self.objects_ref = {}

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
        
    def get_rect(self):
        rect = cell.Cell.get_rect(self)
        for k in self.objects_ref:
            o = self.objects_ref[k]
            rect = rect.union(o.get_rect())

        rect[2] += 10 + self.parent.d_input +  + self.parent.d_output
        rect[3] += 10   
        
        return rect
            
    def set_pos(self, pos):
        dx = pos[0] - self.x 
        dy = pos[1] - self.y 
        self.x = pos[0]
        self.y = pos[1]
        
        for k in self.objects_ref:
            o = self.objects_ref[k]
            rect = o.get_rect()
            o.set_pos((rect[0] + dx, rect[1] + dy))
            
    def draw_text(self, text, rect):
        self.parent.draw_text(text, rect)
        
    def draw_line(self, start, end, color):
        self.parent.draw_line(start, end, color)
        
    def __getattr__(self, key):
        if key == "__nonzero__":
            return True
        
        return self.parent.__dict__[key]
        
    def calc(self, pin):
        if pin in self.objects_ref:
            o = self.objects_ref[pin]
            return o.input("A")
        
        return 0
        
    def parse(self, arr):
        self.parent.read_file(arr[4] + ".txt", self)
        
        for k in self.objects:
            o = self.objects_ref[k]
            if o.type == "output":
                self.outputs.append(k)
            if o.type == "input":
                self.inputs.append(k)    
                o.set_module(self)            
                
        dx = self.x + self.parent.d_input
        dy = self.y 
        
        for k in self.objects_ref:
            o = self.objects_ref[k]
            rect = o.get_rect()
            o.set_pos((rect[0] + dx, rect[1] + dy))

        
        for i in range(len(arr) - 5):
            name =  arr[5 + i]
            if name == "GND":
                conn = None, 0
            elif name == "VCC":
                conn = None, 1
            else:
                conn = self.parent.find_cell_pin(name)
            self.set_free_input(*conn)
            
    def draw(self):
        cell.Cell.draw(self)
        for k in self.objects:
            self.objects_ref[k].draw()
        
    def tick(self):
        cell.Cell.tick(self)
        for k in self.objects:
            self.objects_ref[k].tick()        
        
    def reset(self):
        for k in self.objects:
            self.objects_ref[k].reset()     

class module_input(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.outputs.append("Y")

    def set_module(self, module):
        self.module = module
    
    def calc(self, pin):
        return self.module.input(self.name)
    
    def draw(self):
        cell.Cell.draw(self)
        self.parent.draw_text("IN", self.get_rect())     

class module_output(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.inputs.append("A")

    
    def draw(self):
        cell.Cell.draw(self)
        self.parent.draw_text("OUT", self.get_rect())     
        