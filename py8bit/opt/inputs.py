import cell

class Constant(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.val = 0
        
        self.add_output("Y")

    def parse_cfg(self, arr):
        if len(arr) == 5:
            self.val = int(arr[4])

    def calc(self, pin):
        if pin == "Y":
            return self.val
        
    def update_body(self):
        cell.Cell.update_body(self, self.val)
        self.draw_text(self.name, self.rect_rel)         

        
class Toggle(Constant):
    def click(self):
        self.val = not self.val
        self.update_body()

