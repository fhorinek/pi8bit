import cell


class HexDisplay(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.add_input("A0")
        self.add_input("A1")
        self.add_input("A2")
        self.add_input("A3")
        self.add_input("A4")
        self.add_input("A5")
        self.add_input("A6")
        self.add_input("A7")
        self.old_value = 0
        
    def tick(self):
        val  = self.input("A0") * 1
        val += self.input("A1") * 2
        val += self.input("A2") * 4
        val += self.input("A3") * 8
        val += self.input("A4") * 16
        val += self.input("A5") * 32
        val += self.input("A6") * 64
        val += self.input("A7") * 128        
        if (self.old_value is not val):
            self.old_value = val
            self.update_body()
                    
    def update_body(self):
        cell.Cell.update_body(self)

        val  = self.input("A0") * 1
        val += self.input("A1") * 2
        val += self.input("A2") * 4
        val += self.input("A3") * 8
        val += self.input("A4") * 16
        val += self.input("A5") * 32
        val += self.input("A6") * 64
        val += self.input("A7") * 128
                
        self.parent.draw_text(self.surface, "%02X" % val, self.rect_rel)
        
class Led(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.add_input("A")
        self.old_value = 0
        
    def tick(self):
        if (self.old_value is not self.input("A")):
            self.old_value = self.input("A")
            self.update_body()
        
    def update_body(self):
        cell.Cell.update_body(self, state = self.input("A"))
        self.parent.draw_text(self.surface, self.name, self.rect_rel)
