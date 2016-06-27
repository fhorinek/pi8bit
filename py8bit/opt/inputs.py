import cell

class Toggle(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.val = 0
        
        self.add_output("Y")

    def parse_cfg(self, arr):
       
        if len(arr) == 4:
            self.val = int(arr[3])

    def calc(self, pin):
        if pin == "Y":
            return self.val
        
    def update_body(self):
        cell.Cell.update_body(self, self.val)
        self.parent.draw_text(self.surface, self.name, self.rect_rel)         

    def click(self):
        self.val = not self.val
        self.update_body()

    def get_params(self):
        arr = cell.Cell.get_params(self)
        return [arr[0], str(int(self.val))]
    
class Clock(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.clk = 0
        self.max = 20
        self.val = 0
        self.last_val = 1
        
        self.add_input("R")
        self.add_input("E")
                
        self.add_output("Y")

    def tick(self):
        cell.Cell.tick(self)
        
        if self.input("E"):
            self.clk = (self.clk + 1) % (self.max * 2)

        if self.input("R"):
            self.clk = 0
            
        self.val = int(self.clk > self.max)
        if self.val <> self.last_val:
            self.update_body()
            self.last_val = self.val

    def calc(self, pin):
        if pin == "Y":
            return self.val
        
    def update_body(self):
        cell.Cell.update_body(self, self.val)
        self.parent.draw_text(self.surface, "clk", self.rect_rel)    