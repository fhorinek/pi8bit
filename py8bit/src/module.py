import cell

class module(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.objects = []
        self.objects_ref = {}
        self.module = True
        self.rect = False

    def read_file(self, filename, owner):
        self.parent.read_file(filename, owner)

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
        
    def update_rect(self):
        rect = cell.Cell.get_rect(self)
        for k in self.objects_ref:
            o = self.objects_ref[k]
            rect = rect.union(o.get_rect())

        rect[2] += 10 + self.parent.d_input +  + self.parent.d_output
        rect[3] += 10   
        
        self.rect = rect
            
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
        
    def __str__(self):
        return 
            
    def __getattr__(self, key):
        if key == "__nonzero__":
            return True

        root = self.parent
        while (True):
            if root.module == False:
                break
            root = root.parent
    
        return root.__dict__[key]

        
    def calc(self, pin):
        if pin in self.objects_ref:
            o = self.objects_ref[pin]
            return o.input("A")
        
        return 0
        
    def get_params(self):
        arr = []
        arr.append(self.filename)
        return arr + cell.Cell.get_params(self)
        
    def parse(self, arr):
        self.filename = arr[4]
        self.parent.read_file(self.filename + ".txt", self)
        
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
            
        self.update_rect()
            
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
        self.module = False

    def set_module(self, module):
        self.module = module
    
    def calc(self, pin):
        if self.module is False:
            return 0
        else:
            return self.module.input(self.name)
    
    def draw(self):
        cell.Cell.draw(self)
        self.parent.draw_text(self.name, self.get_rect())     


class module_output(cell.Cell):
    def __init__(self, parent, rect):
        cell.Cell.__init__(self, parent, rect)
        self.inputs.append("A")
    
    def draw(self):
        cell.Cell.draw(self)
        self.parent.draw_text(self.name, self.get_rect())     
        