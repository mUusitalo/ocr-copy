import tkinter as tk
from desktopmagic.screengrab_win32 import getRectAsImage

from monitor import *
from pos2 import Pos2

ALPHA = 0.5

class _App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.init_tk()
        self.frame = None
        self.pos1_relative = None
        self.pos1_absolute = None
        self.pos2_absolute = None
        self.update_geometry()

    def init_tk(self):
        self.overrideredirect(1)
        self.attributes('-topmost', True)
        self.config(bg='white')
        self.wm_attributes("-alpha", ALPHA)
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry('{}x{}+{}+{}'.format(str(self.screen_width), str(self.screen_height), str(0), str(0)))
        
        #tkinter events
        self.bind('<Button-1>', self.on_click)
        self.bind('<ButtonRelease-1>', self.on_release)
        self.bind('<Motion>', self.on_move)
        self.focus_force()

    def on_click(self, event): #grabs pos1 and initializes the frame
        self.pos1_relative = Pos2(event.x, event.y) #For tkinter
        self.pos1_absolute = Pos2(self.winfo_pointerx(), self.winfo_pointery()) #For screenshot

    def on_move(self, event): #updates the frame
        if not self.pos1_relative: return
        if self.frame:
            self.frame.destroy()
        pos = Pos2(event.x, event.y)
        diff = self.pos1_relative-pos
        self.frame = tk.Frame(master=self, width=abs(diff.x), height=abs(diff.y), bg="black")
        self.frame.place(x=self.pos1_relative[0] if diff.x < 0 else self.pos1_relative.x - diff.x,
                         y=self.pos1_relative[1] if diff.y < 0 else self.pos1_relative[1] - diff.y)

    def on_release(self, event): #grabs pos2 and destroys the _App
        self.pos2_absolute = Pos2(self.winfo_pointerx(), self.winfo_pointery())
        self.destroy()

    def exit(self, _):
        print("exit function called")
        self.destroy()

    def update_geometry(self): #Checks which monitor the cursor is on
        self.focus_set()
        self.focus_force()
        monitor = MonitorHandler.find_new_monitor(Pos2(self.winfo_pointerx(), self.winfo_pointery()))
        self.geometry('{}x{}+{}+{}'.format(str(monitor.width), str(monitor.height), str(monitor.x), str(monitor.y)))
        self.after(5, self.update_geometry)

def _sort_coords(pos1, pos2):
    if pos1 == None or pos2 == None:
        raise ValueError("(pos1 or pos2) = None")
    if pos1 == pos2:
        return (pos1, pos2)
    x_coords, y_coords = map(list, (zip(pos1, pos2)))
    x_coords.sort()
    y_coords.sort()
    return zip(x_coords, y_coords)

def _run_tkinter(exit_hotkey = None): #Initialises tkinter loop and starts the loop. Returns pos1 and pos2
    app = _App()
    if exit_hotkey:
        app.bind(exit_hotkey, app.exit)
    app.mainloop()
    return app.pos1_absolute, app.pos2_absolute

def grab(exit_hotkey = None):
    pos1, pos2 = _run_tkinter(exit_hotkey)
    pos1, pos2 = _sort_coords(list(pos1), list(pos2))
    if pos1 == pos2: return None
    image = getRectAsImage((pos1[0], pos1[1], pos2[0], pos2[1])) # BUG, breaks with Window's content scaling
    #image.show() # For debugging
    return image # in PIL format