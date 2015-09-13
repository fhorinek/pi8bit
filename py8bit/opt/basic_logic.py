import cell
        
class And(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.add_output("Y")
        self.add_input("A")
        self.add_input("B")
        
    def calc(self, pin):
        if pin == "Y":
            return self.input("A") & self.input("B")
        
    def update_body(self):
        cell.Cell.update_body(self)
        self.draw_text("AND", self.rect_rel)  
        
class Or(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.add_output("Y")
        self.add_input("A")
        self.add_input("B")
        
    def calc(self, pin):
        if pin == "Y":
            return self.input("A") | self.input("B")
        
    def update_body(self):
        cell.Cell.update_body(self)
        self.draw_text("OR", self.rect_rel)  

class Xor(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.add_output("Y")
        self.add_input("A")
        self.add_input("B")
        
    def calc(self, pin):
        if pin == "Y":
            return self.input("A") ^ self.input("B")
        
    def update_body(self):
        cell.Cell.update_body(self)
        self.draw_text("XOR", self.rect_rel)  
        
class Nand(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.add_output("Y")
        self.add_input("A")
        self.add_input("B")
        
    def calc(self, pin):
        if pin == "Y":
            return not (self.input("A") & self.input("B"))
        
    def update_body(self):
        cell.Cell.update_body(self)
        self.draw_text("NAND", self.rect_rel) 
        
class Nor(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.add_output("Y")
        self.add_input("A")
        self.add_input("B")
        
    def calc(self, pin):
        if pin == "Y":
            return not (self.input("A") | self.input("B"))
        
    def update_body(self):
        cell.Cell.update_body(self)
        self.draw_text("NOR", self.rect_rel)        
        
class Not(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.add_output("Y")
        self.add_input("A")
        
    def calc(self, pin):
        if pin == "Y":
            return not self.input("A")
        
    def update_body(self):
        cell.Cell.update_body(self)
        self.draw_text("NOT", self.rect_rel)   