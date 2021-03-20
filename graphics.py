import tkinter as tk
from desktopmagic.screengrab_win32 import getRectAsImage

from monitor import *
from pos2 import Pos2

ALPHA = 0.2

class _App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.exit_ = False
        self.init_tk()
        self.frame = None
        self.pos1_relative = None
        self.pos1_absolute = None
        self.pos2_absolute = None
        self.update_geometry()

    def init_tk(self):
        self.overrideredirect(1)
        self.config(bg='white')
        self.wm_attributes("-alpha", ALPHA)
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.geometry('{}x{}+{}+{}'.format(str(self.screen_width), str(self.screen_height), str(0), str(0)))
        self.attributes('-topmost', True)
        self.focus_force()
        self.grab_set()

        
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
        self.exit()

    def exit(self):
        print("exit function called")
        self.exit_ = True
        self.destroy()

    def update_geometry(self): #Checks which monitor the cursor is on
        if self.exit_: return
        self.focus_set()
        self.focus_force()
        monitor = MonitorHandler.find_new_monitor(Pos2(self.winfo_pointerx(), self.winfo_pointery()))
        self.geometry('{}x{}+{}+{}'.format(str(monitor.width), str(monitor.height), str(monitor.x), str(monitor.y)))
        self.after(5, self.update_geometry)

def _run_tkinter(): #Initialises tkinter loop and starts the loop. Returns pos1 and pos2
    app = _App()
    app.bind('<Escape>', app.exit)
    app.mainloop()
    return app.pos1_absolute, app.pos2_absolute

def _sort_coords(pos_tuple):
    coordinates = map(sorted, (zip(*pos_tuple)))
    return (Pos2(*l) for l in zip(*coordinates))

def grab():
    try:
        pos1, pos2 = _sort_coords(_run_tkinter())
        image = getRectAsImage((*pos1, *pos2)).convert('L') # BUG, breaks with Window's content scaling
        #image.show() # For debugging
        return image # in PIL format
    except:
        return None

if __name__ == '__main__':
    grab()