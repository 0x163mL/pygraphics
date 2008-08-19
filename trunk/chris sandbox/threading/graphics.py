import time, os, sys
import Tkinter as tk

##########################################################################
# Module Exceptions

import exceptions

class GraphicsError(exceptions.Exception):
    """Generic error class for graphics module exceptions."""
    def __init__(self, args=None):
        self.args=args

OBJ_ALREADY_DRAWN = "Object currently drawn"
UNSUPPORTED_METHOD = "Object doesn't support operation"
BAD_OPTION = "Illegal option value"
DEAD_THREAD = "Graphics thread quit unexpectedly"

###########################################################################
# Support to run Tk in a separate thread

from copy import copy
from Queue import Queue
import thread
import atexit


_tk_request = Queue(0)
_tk_result = Queue(1)
_POLL_INTERVAL = 10

_root = None
_thread_running = True
_exception_info = None

def _tk_thread():
    global _root
    _root = tk.Tk()
    _root.withdraw()
    _root.after(_POLL_INTERVAL, _tk_pump)
    _root.mainloop()

def _tk_pump():
    global _thread_running
    while not _tk_request.empty():
        command,returns_value = _tk_request.get()
        try:
            result = command()
            if returns_value:
                _tk_result.put(result)
        except:
            _thread_running = False
            if returns_value:
                _tk_result.put(None) # release client
            raise # re-raise the exception -- kills the thread
    if _thread_running:
        _root.after(_POLL_INTERVAL, _tk_pump)

def _tkCall(f, *args, **kw):
    # execute synchronous call to f in the Tk thread
    # this function should be used when a return value from
    #   f is required or when synchronizing the threads.
    # call to _tkCall in Tk thread == DEADLOCK !
    if not _thread_running:
        raise GraphicsError, DEAD_THREAD
    def func():
        return f(*args, **kw)
    _tk_request.put((func,True),True)
    result = _tk_result.get(True)
    return result

# .nah. Added these so that these functions can be exported
tkCall = _tkCall

def _tkExec(f, *args, **kw):
    # schedule f to execute in the Tk thread. This function does
    #   not wait for f to actually be executed.
    #global _exception_info
    #_exception_info = None
    if not _thread_running:
        raise GraphicsError, DEAD_THREAD
    def func():
        return f(*args, **kw)
    _tk_request.put((func,False),True)
    #if _exception_info is not None:
    #    raise GraphicsError, "Invalid Operation: %s" % str(_exception_info)

# .nah. Added these so that these functions can be exported
tkExec = _tkExec

def _tkShutdown():
    # shutdown the tk thread
    global _thread_running
    #_tkExec(sys.exit)
    _thread_running = False
    time.sleep(.5) # give tk thread time to quit

# Fire up the separate Tk thread
thread.start_new_thread(_tk_thread,())

# Kill the tk thread at exit
atexit.register(_tkShutdown)

############################################################################
# Graphics classes start here
        
class PictureWindow(tk.Canvas):
    """A PictureWindow is a toplevel window for displaying graphics."""

    def __init__(self, title="Graphics Window",
                 width=200, height=200, autoflush=False):
        
        _tkCall(self.__init_help, title, width, height, autoflush)
 
    
    def __init_help(self, title, width, height, autoflush):
        
        master = tk.Toplevel(_root)
        master.protocol("WM_DELETE_WINDOW", self.__close_help)
        tk.Canvas.__init__(self, master, width=width, height=height)
        self.master.title(title)
        self.pack()
        #master.resizable(0,0)
        self.foreground = "black"
        self.items = []
        self.mouseX = None
        self.mouseY = None
        self.bind("<Button-1>", self._onClick)
        self.height = height
        self.width = width
        self.autoflush = autoflush
        self._mouseCallback = None
        self.trans = None
        self.closed = False
        if autoflush: _root.update()


    def __checkOpen(self):
        if self.closed:
            raise GraphicsError, "window is closed"


    def setBackground(self, color):
        """Set background color of the window"""
        self.__checkOpen()
        _tkExec(self.config, bg=color)
        
    def setCoords(self, x1, y1, x2, y2):
        """Set coordinates of window to run from (x1,y1) in the
        lower-left corner to (x2,y2) in the upper-right corner."""
        self.trans = Transform(self.width, self.height, x1, y1, x2, y2)


    def close(self):
        if self.closed: return
        _tkCall(self.__close_help)
        
        
    def __close_help(self):
        """Close the window"""
        self.closed = True
        self.master.destroy()
        _root.update()

    def isClosed(self):
        return self.closed

    def __autoflush(self):
        if self.autoflush:
            _tkCall(_root.update)
    
    def plot(self, x, y, color="black"):
        """Set pixel (x,y) to the given color"""
        self.__checkOpen()
        xs,ys = self.toScreen(x,y)
        #self.create_line(xs,ys,xs+1,ys, fill=color)
        _tkExec(self.create_line,xs,ys,xs+1,ys,fill=color)
        self.__autoflush()
        
    def plotPixel(self, x, y, color="black"):
        """Set pixel raw (independent of window coordinates) pixel
        (x,y) to color"""
        self.__checkOpen()
    	#self.create_line(x,y,x+1,y, fill=color)
        _tkExec(self.create_line, x,y,x+1,y, fill=color)
        self.__autoflush()
    	
    def flush(self):
        """Update drawing to the window"""
        #self.update_idletasks()
        self.__checkOpen()
        _tkCall(self.update_idletasks)
        
    def getMouse(self):
        """Wait for mouse click and return Point object representing
        the click"""
        self.mouseX = None
        self.mouseY = None
        while self.mouseX == None or self.mouseY == None:
            #self.update()
            _tkCall(self.update)
            if self.isClosed(): raise GraphicsError, "getMouse in closed window"
            time.sleep(.1) # give up thread
        x,y = self.toWorld(self.mouseX, self.mouseY)
        self.mouseX = None
        self.mouseY = None
        return WindowPoint(x,y)

    def checkMouse(self):
        """Return mouse click last mouse click or None if mouse has
        not been clicked since last call"""
        if self.isClosed():
            raise GraphicsError, "checkMouse in closed window"
        _tkCall(self.update)
        if self.mouseX != None and self.mouseY != None:
            x,y = self.toWorld(self.mouseX, self.mouseY)
            self.mouseX = None
            self.mouseY = None
            return WindowPoint(x,y)
        else:
            return None
            
    def getHeight(self):
        """Return the height of the window"""
        return self.height
        
    def getWidth(self):
        """Return the width of the window"""
        return self.width
    
    def toScreen(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.screen(x,y)
        else:
            return x,y
                      
    def toWorld(self, x, y):
        trans = self.trans
        if trans:
            return self.trans.world(x,y)
        else:
            return x,y
        
    def setMouseHandler(self, func):
        self._mouseCallback = func
        
    def _onClick(self, e):
        self.mouseX = e.x
        self.mouseY = e.y
        if self._mouseCallback:
            self._mouseCallback(WindowPoint(e.x, e.y)) 
                      
class Transform(object):

    """Internal class for 2-D coordinate transformations"""
    
    def __init__(self, w, h, xlow, ylow, xhigh, yhigh):
        # w, h are width and height of window
        # (xlow,ylow) coordinates of lower-left [raw (0,h-1)]
        # (xhigh,yhigh) coordinates of upper-right [raw (w-1,0)]
        xspan = (xhigh-xlow)
        yspan = (yhigh-ylow)
        self.xbase = xlow
        self.ybase = yhigh
        self.xscale = xspan/float(w-1)
        self.yscale = yspan/float(h-1)
        
    def screen(self,x,y):
        # Returns x,y in screen (actually window) coordinates
        xs = (x-self.xbase) / self.xscale
        ys = (self.ybase-y) / self.yscale
        return int(xs+0.5),int(ys+0.5)
        
    def world(self,xs,ys):
        # Returns xs,ys in world coordinates
        x = xs*self.xscale + self.xbase
        y = self.ybase - ys*self.yscale
        return x,y


# Default values for various item configuration options. Only a subset of
#   keys may be present in the configuration dictionary for a given item
DEFAULT_CONFIG = {"fill":"",
		  "outline":"black",
		  "width":"1",
		  "arrow":"none",
		  "text":"",
		  "justify":"center",
                  "font": ("helvetica", 12, "normal")}

class GraphicsObject(object):

    """Generic base class for all of the drawable objects"""
    # A subclass of GraphicsObject should override _draw and
    #   and _move methods.
    
    def __init__(self, options):
        # options is a list of strings indicating which options are
        # legal for this object.
        
        # When an object is drawn, canvas is set to the GraphWin(canvas)
        #    object where it is drawn and id is the TK identifier of the
        #    drawn shape.
        self.canvas = None
        self.id = None

        # config is the dictionary of configuration options for the widget.
        config = {}
        for option in options:
            config[option] = DEFAULT_CONFIG[option]
        self.config = config
        
    def setFill(self, color):
        """Set interior color to color"""
        self._reconfig("fill", color)
        
    def setOutline(self, color):
        """Set outline color to color"""
        self._reconfig("outline", color)
        
    def setWidth(self, width):
        """Set line weight to width"""
        self._reconfig("width", width)

    def draw(self, graphwin):

        """Draw the object in graphwin, which should be a GraphWin
        object.  A GraphicsObject may only be drawn into one
        window. Raises an error if attempt made to draw an object that
        is already visible."""

        if self.canvas and not self.canvas.isClosed(): raise GraphicsError, OBJ_ALREADY_DRAWN
        if graphwin.isClosed(): raise GraphicsError, "Can't draw to closed window"
        self.canvas = graphwin
        #self.id = self._draw(graphwin, self.config)
        self.id = _tkCall(self._draw, graphwin, self.config)
        if graphwin.autoflush:
            #_root.update()
            _tkCall(_root.update)

    def undraw(self):

        """Undraw the object (i.e. hide it). Returns silently if the
        object is not currently drawn."""
        
        if not self.canvas: return
        if not self.canvas.isClosed():
            #self.canvas.delete(self.id)
            _tkExec(self.canvas.delete, self.id)
            if self.canvas.autoflush:
                #_root.update()
                _tkCall(_root.update)
        self.canvas = None
        self.id = None

    def move(self, dx, dy):

        """move object dx units in x direction and dy units in y
        direction"""
        
        self._move(dx,dy)
        canvas = self.canvas
        if canvas and not canvas.isClosed():
            trans = canvas.trans
            if trans:
                x = dx/ trans.xscale 
                y = -dy / trans.yscale
            else:
                x = dx
                y = dy
            #self.canvas.move(self.id, x, y)
            _tkExec(self.canvas.move, self.id, x, y)
            if canvas.autoflush:
                #_root.update()
                _tkCall(_root.update)
           
    def _reconfig(self, option, setting):
        # Internal method for changing configuration of the object
        # Raises an error if the option does not exist in the config
        #    dictionary for this object
        if not self.config.has_key(option):
            raise GraphicsError, UNSUPPORTED_METHOD
        options = self.config
        options[option] = setting
        if self.canvas and not self.canvas.isClosed():
            #self.canvas.itemconfig(self.id, options)
            _tkExec(self.canvas.itemconfig, self.id, options)
            if self.canvas.autoflush:
                #_root.update()
                _tkCall(_root.update)

    def _draw(self, canvas, options):
        """draws appropriate figure on canvas with options provided
        Returns Tk id of item drawn"""
        pass # must override in subclass

    def _move(self, dx, dy):
        """updates internal state of object to move it dx,dy units"""
        pass # must override in subclass
         
class WindowPoint(GraphicsObject):
    
    def __init__(self, x, y):
        GraphicsObject.__init__(self, ["outline", "fill"])
        self.setFill = self.setOutline
        self.x = x
        self.y = y
        
        
    def _draw(self, canvas, options):
        x,y = canvas.toScreen(self.x,self.y)
        return canvas.create_rectangle(x,y,x+1,y+1,options)
        
        
    def _move(self, dx, dy):
        self.x = self.x + dx
        self.y = self.y + dy
        
        
    def clone(self):
        other = WindowPoint(self.x,self.y)
        other.config = self.config.copy()
        return other
            
                
    def getX(self): return self.x
    def getY(self): return self.y


class WindowImage(GraphicsObject):

    id_count = 0
    image_cache = {} # tk photoimages go here to avoid GC while drawn 
    
    def __init__(self, point, image):
        
        GraphicsObject.__init__(self, [])
        self.anchor = point.clone()
        self.image_id = WindowImage.id_count
        WindowImage.id_count += 1
        self.img = image


    def _draw(self, canvas, options):
        
        p = self.anchor
        x,y = canvas.toScreen(p.x, p.y)
        self.image_cache[self.image_id] = self.img # save a reference  
        return canvas.create_image(x, y, image=self.img)
    
    
    def _move(self, dx, dy):
        
        self.anchor.move(dx,dy)
    
    
    def get_height(self):
        
        height = _tkCall(self.img.height)
        return height
        
        
    def get_width(self):
        
        width = _tkCall(self.img.width)
        return width

    
    def undraw(self):
        
        del self.image_cache[self.image_id]  # allow gc of tk photoimage
        GraphicsObject.undraw(self)


    def get_anchor(self):
        
        return self.anchor.clone()
    		
            
    def clone(self):
        
        img_copy = _tkCall(self.img.copy)
        other = WindowImage(self.anchor, img_copy)
        other.config = self.config.copy()
        return other
        
        
if __name__ == "__main__":
    import picture
    import ImageTk
    
    class ShowPicture(picture.Picture):
        
        def _make_window(self, x, y):
            
            title = 'File: %s' % self.get_filename()
            self.win = PictureWindow(title=title, width=x, height=y)
            self.win.setCoords(0, y - 1, x - 1, 0)
        
        
        def _draw_image_to_win(self, win):
            
            width = win.getWidth()
            height = win.getHeight()
            self.showim = WindowImage(WindowPoint(width/2, height/2), ImageTk.PhotoImage(self.get_image()))
            self.showim.draw(win)
            

        def show(self):
            
            if self.win:
                self.win.close()
            width = self.get_width()
            height = self.get_height()
            self._make_window(width, height + 20)
            self._draw_image_to_win(self.win)
            
        def update(self):
            
            if self.win and self.showim:
                width = self.get_width()
                height = self.get_height()
                self.showim.undraw()
                self._draw_image_to_win(self.win)
    
    pic = ShowPicture(filename='/Users/chris/Pictures/chickadee.jpg')
    pic.win = None
    pic.show()