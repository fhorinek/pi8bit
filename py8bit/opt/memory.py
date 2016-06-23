import cell
import utils
from pygame import Rect
import os

class Memory(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.file = False
        self.filename = "[no file]"
        self.data = 0
        self.address = 0
        
        for i in range(16):
            self.add_input("A%u" % i)

        for i in range(8):
            self.add_input("Di%u" % i)
            
        self.add_input("W")
        self.add_input("E")
            
        for i in range(8):
            self.add_output("Do%u" % i)
            

    def parse_cfg(self, arr):
        if len(arr) >= 4:
            self.open_file(arr[3])
            del arr[3]
            
        cell.Cell.parse_cfg(self, arr)
            
       
    def open_file(self, filename):
        if filename == "__none__":
            return
        
        self.filename = filename
           
        try:
            if not os.path.exists(self.filename):
                f = open(self.filename, "wb")
                f.close()
            
            f = open(self.filename, "rb")
            self.bin_data = map(ord, list(f.read()))
            f.close()            

            if len(self.bin_data) < 0x10000:
                self.bin_data += [0] * (0x10000 - len(self.bin_data))
            
            if len(self.bin_data) > 0x10000:
                self.bin_data = self.bin_data[0:0x10000]
 
            self.file = True
        except:
            self.file = False
            self.filename = "[error]"
            
        self.update_body()

    def tick(self):
        if self.file == False:
            return

        adr = 0
        need_update = False
        
        for i in range(16):
            adr += int(self.input("A%u" % i)) * (1 << i)

        if adr <> self.address:
            self.data = self.bin_data[adr]
            self.address = adr
            need_update = True
        
        if self.input("W"):
            data_in = 0
            for i in range(8):
                data_in += int(self.input("Di%u" % i)) * (1 << i)  
            if data_in <> self.data:
                self.bin_data[adr] = data_in
                self.data = data_in
                need_update = True

        if need_update:
            self.update_body()
            
        cell.Cell.tick(self)
        
    def calc(self, pin):
        if self.input("E"):
            for i in range(8):
                if pin == "Do%u" % i:
                    return (self.data & (1 << i)) <> 0    
                
        return 0

    def update_rect(self):
        cell.Cell.update_rect(self)
        self.rect.w *= 3
        self.rect_rel.w *= 3

    def update_body(self):
        cell.Cell.update_body(self)
        
        h = int(self.rect_rel.height / 4);
        pos = Rect(self.rect_rel)
        pos.height = h
        self.parent.draw_text(self.surface, "MEMORY", pos)
        
        pos = Rect(self.rect_rel)
        pos.y = h * 1
        pos.height = h
        self.parent.draw_text(self.surface, self.filename, pos)
        
        pos = Rect(self.rect_rel)
        pos.y = h * 2
        pos.height = h
        self.parent.draw_text(self.surface, "address: %04X" % self.address, pos)

        pos = Rect(self.rect_rel)
        pos.y = h * 3
        pos.height = h
        self.parent.draw_text(self.surface, "data: %02X" % self.data, pos)

    def click(self):
        self.open_file(utils.file_opendialog())
        

    def get_params(self):
        if self.file:
            f = open(self.filename, "wb")
            f.write("".join(map(chr, self.bin_data)))
            f.close()              
        
        arr = cell.Cell.get_params(self)
        if self.file:
            return [arr[0], self.filename] + arr[1:]
        else:
            return [arr[0], "__none__"] + arr[1:]
        