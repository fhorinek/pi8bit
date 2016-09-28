import cell
from pygame import Rect

class Fcell(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.line_height = 1
        
    def update_rect(self):
        self.rect.w = self.parent.canvas.style["d_width"]
        self.rect.h = self.parent.canvas.style["d_line"] * (self.line_height + 1)

        self.rect_rel = Rect(self.rect)
        self.rect_rel.x = 0
        self.rect_rel.y = 0
        self.update_io_xy()
        
    def update_body(self, state = None):
        rect = Rect(0, 0, self.rect.w, self.rect.h)
        
        self.surface = self.parent.mk_surface(self.rect)
        color = "c_fill"

                
        self.parent.draw_rect(self.surface, self.parent.canvas.style[color], rect)
        self.parent.draw_rect(self.surface, self.parent.canvas.style["c_border"], rect, 2)
        
        top_rect = Rect(0, 0, self.rect.w,  self.parent.canvas.style["d_line"])
        
        self.parent.draw_rect(self.surface, self.parent.canvas.style["c_border"], top_rect, 1)
        self.parent.draw_text(self.surface, self.name, top_rect)
       
        self.request_redraw()