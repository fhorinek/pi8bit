import cell
import pygame

class Node(cell.Cell):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.net = False
        self.siblings = []
        self.add_output("Y")

    def parse_cfg(self, arr):
        net_name = arr[3]
        self.net = self.parent.find_cell(net_name)
        if self.net is False:
            self.net = self.parent.add_net(net_name)

        for i in range(len(arr) - 4):
            obj, pin = self.parent.find_cell_pin(arr[4 + i])
            if isinstance(obj, Node):
                self.siblings.append(obj)
            else:
                self.assign_free_input(obj, pin)

        self.net.add_node(self)

    def assign_input(self, name, in_cell, in_pin):
        self.inputs[name] = [in_cell, in_pin]
        self.update_io_xy()
        
    def assign_free_input(self, in_cell, in_pin):
        pin = "__in_%d" % len(self.inputs)
        self.assign_input(pin, in_cell, in_pin)        
        
    def get_params(self):
        p = cell.Cell.get_params(self)
        p.insert(1, self.net.name)
        for o in self.siblings:
            p.append(o.name)
            
        return p
      
    def update_rect(self):
        self.rect.w = self.parent.canvas.style["d_line"]
        self.rect.h = self.parent.canvas.style["d_line"]
   
      
    def update_body(self, state=None): pass
    def draw(self): pass
    def draw_io(self): pass
    def calc(self, pin): pass
    
    def update_io_xy(self):
        self.output_xy["Y"] = [self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2]
        self.parent.canvas.request_io_redraw()
       
    def output(self, pin):
        if self.net:
            return self.net.output(pin)
        else:
            return 0
       
    def draw_node(self, state):
        start = self.output_xy["Y"]
#         if len(self.siblings) + len(self.inputs) + self.have_output <> 2:
        self.parent.draw_circle(start, state)
          
        for n in self.siblings:
            end = n.output_xy["Y"]
            self.parent.draw_line(start, end, state) 
            
        for c in self.inputs:
            if self.inputs[c] is not False:
                in_obj, in_pin = self.inputs[c]
                if not isinstance(in_obj, cell.Invisible):
                    end = in_obj.output_xy[in_pin]
                    self.parent.draw_line(start, end, state)             

    def add_sibling(self, node):
        if node not in self.siblings:
            self.siblings.append(node)


    def remove_sibling(self, node):
        if node in self.siblings:
            self.siblings.remove(node)

    def disconnect(self):
        cell.Cell.disconnect(self)
        for n in self.net.list_node_sibling(self):
            n.remove_sibling(self)
        
        self.net.nodes.remove(self)
        self.net.rebuild()
        
    def check_input_line_collision(self, pos):
        for p in self.inputs:
            if self.inputs[p]:
                obj, pin = self.inputs[p]
                if isinstance(obj, cell.Invisible):
                    continue

                start = self.output_xy["Y"]
                end = obj.output_xy[pin]
                #basic rect TODO
                offset = self.parent.canvas.style["d_line_col"]
                
                x = min((start[0], end[0])) - offset
                y = min((start[1], end[1])) - offset
                w = abs(start[0] - end[0]) + offset * 2
                h = abs(start[1] - end[1]) + offset * 2
                
                basic = pygame.Rect(x, y, w, h)
                
                if basic.collidepoint(pos):
                
                    dx = end[0] - start[0]
                    dy = end[1] - start[1]
                    if abs(dx) < abs(dy):
                        k = float(dx) / float(dy)
                        x = start[0] + k * (pos[1] - start[1])
                
                        if abs(x - pos[0]) < offset:
                            return self, p, obj, pin                      
                    else:
                        k = float(dy) / float(dx)
                        y = start[1] + k * (pos[0] - start[0])
                        
                        if abs(y - pos[1]) < offset:
                            return self, p, obj, pin
        return False 
        


class Net(cell.Invisible):
    def __init__(self, parent):
        cell.Cell.__init__(self, parent)
        self.add_output("Y")
        self.nodes = []

    def add_node(self, node):
        if self is not node.net:
            node.net = self
            
        if node not in self.nodes:
            self.nodes.append(node)

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)        

    def update_rect(self): pass
    def update_body(self, state=None): pass
    def update_io_xy(self): pass
    def draw(self): pass  
    def parse_cfg(self, arr): pass
    def check_input_line_collision(self, pos): return False
    
    def list_node_sibling(self, node):
        ret = list(node.siblings)
        for n in self.nodes:
            if node in n.siblings:
                if n not in ret:
                    ret.append(n)
                    continue
        return ret
    
    def rebuild_r(self, node, visited, group):
        if node in visited:
            return
        
        visited.append(node)
        group.append(node)     
        for sib in self.list_node_sibling(node):
            self.rebuild_r(sib, visited, group)
            
    
    def rebuild(self):
        groups = []
        visited = []
        
        for node in self.nodes:
            if node in visited:
                continue
                         
            group = []
            self.rebuild_r(node, visited, group)

            print len(group), ":", 
            for g in group:
                print g.name,
            print
            groups.append(group)
            
            
        for i in range(1, len(groups)):
            group = groups[i]
            net = self.parent.add_net()
            
            for node in group:
                self.remove_node(node)
                node.net = net
                net.add_node(node)
            
    def asimilate(self, net):
        if net == self:
            return
        for node in net.nodes:
            self.add_node(node)
        net.nodes = []
        self.parent.delete(net.name)
    
    def get_params(self):
        return False
    
    def calc(self, pin):
        ret = 0
        for node in self.nodes:
            for pin in node.inputs:
                ret = ret | node.input(pin)
        
        return ret
            
    def draw_io(self):   
        state = self.output("Y")        
        if self.input_cache == state:
            pass
        self.input_cache = state
        
        for node in self.nodes:
            node.draw_node(state)
        

        

