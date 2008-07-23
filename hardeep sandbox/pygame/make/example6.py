from hmake import *
from media import *
import random
from random import randint

class Game(hMain):
    def __init__(self):
        hMain.__init__(self, 'Example 6 :: Gravity v2 :: LMB - Force | RMB - Reset')
        self.start_physics = True
        
    def _get_rand_col(self):
        return (randint(50,100), randint(50,100), randint(200,255))
    
    def init_game(self):
        pygame.mouse.set_visible(False)
    
    # init_physics gets automatically run if start_physics is True!
    def init_physics(self):
        self.set_gravity(0.0, 400.0)
        
        objs_linked = []
        a = ThrowableBall()
        self.add_obj(a)
#        
#        col = (randint(200,255), randint(50,100), randint(50,100))
#        b_1 = LinkBall(a, H_WIN_CENTER_COORDS[0], H_WIN_CENTER_COORDS[1]+20, col)
#        objs_linked.append(b_1)
#        
#        col = (randint(200,255), randint(50,100), randint(50,100))
#        b_2 = LinkBall(b_1, H_WIN_CENTER_COORDS[0], H_WIN_CENTER_COORDS[1]+40, col)
#        objs_linked.append(b_2)       
#        
#        for obj in objs_linked:
#            self.add_obj(obj)
        
        self.add_obj(MouseCursor())
        
        self.add_obj(Ground())
#        size = 50
#        points = [(-size, -size), (-size, size), (size,size), (size, -size)]
#        print 'size', points
#        mass = 10.0
#        moment = pymunk.moment_for_poly(mass, points, (0,0))
#        body = pymunk.Body(mass, moment)
#        body.position = 240, 300
#        shape = pymunk.Poly(body, points, (0,0))
#        shape.friction = 1
#        self.SDL_thread.physical_space.add_static(body,shape)
        
        print self.SDL_thread.physical_space.static_shapes
        print self.SDL_thread.physical_space.shapes
        print self.SDL_thread.physical_space.bodies
        
class Ground(hObj):
    def __init__(self):
        hObj.__init__(self, 'Ground')
        
        self.set_physics = True
        self.set_static = True
        
        self.look = hShape.rectangle(200, 100, (0, 0, 255))
        self.set_pos((240, 300))
        
        self.add_event(H_EVENT_INIT_PHYSICS, self.event_init_physics)
        
    def event_init_physics(self, obj, e):
        self.set_pos((240, 300))
            
class MouseCursor(hObj):
    def __init__(self):
        hObj.__init__(self, 'Mouse')
        
        self.set_physics = False
        self.look = hShape.rectangle(5, 5, (0, 255, 0), width=3)
        
        self.add_event(H_EVENT_MOUSE_MOVE, self.event_mouse_move)
        
    def event_mouse_move(self, obj, e):
        self.set_pos(e.pos)
        
class LinkBall(hObj):
    def __init__(self, parent_obj, x, y, col, size=20):
        hObj.__init__(self, 'LinkBall')
        
        self.col = col
        self.parent_obj = parent_obj
        
        self.set_pos((x, y))
        self.size = size
        
        self.set_visual_data(col)
        self.set_physics = True
        
        self.add_event(H_EVENT_INIT_PHYSICS, self.event_init_physics)
        
    def event_init_physics(self, obj, e):
        self.join = pymunk.SlideJoint(self.body, self.parent_obj.body, 
                                      Vec2d(0,self.size), 
                                      Vec2d(0,self.size * -1), 
                                      1, 
                                      1)
        
        self.physical_shape.friction = 0.0
        self.physical_shape.elasticity = 1.0
        self.physical_space.add(self.join)
        
    def set_visual_data(self, col):
        self.look = hShape.circle(self.size, col)
        
class ThrowableBall(hObj):
    def __init__(self):
        hObj.__init__(self, 'ThrowableBall')
        
        self.set_visual_data()
        self.set_physics = True
        self.set_pos((-1, 10))
        
        self.add_event(H_EVENT_MOUSE_DOWN, self.event_mouse_down)
        self.add_event(H_EVENT_INIT_PHYSICS, self.event_init_physics)
        
    def event_init_physics(self, obj, e):
        self.physical_shape.friction = 0.0
        self.physical_shape.elasticity = 1.0
        
    def event_mouse_down(self, obj, e):
        if e.button == 3:
            self.reset_forces()
            self.set_pos((-1, 10))
        else:
            factor = 6300000
            factor_div = factor / 20
            
            x,y = self.pos
            m_x, m_y = e.pos
            
            f_x = max(min(factor_div, (1/(x - m_x)) * factor), factor_div * -1)
            f_y = max(min(factor_div, (1/(y - m_y)) * factor), factor_div * -1)
            
            self.add_impulse(f_x, f_y, (0,0)) # Treated as a vector (+-x, +-y)
        
    def set_visual_data(self):
        self.look = hShape.circle(40, white, mass_factor=0.01)
        self.set_pos(H_WIN_CENTER)
        
g = Game()
g.start()