import tkinter as tk
from typing import Optional, Iterable
from desktopmagic.screengrab_win32 import getRectAsImage
from PIL.Image import Image

from .monitor import *
from .pos2 import Pos2


ALPHA: float = 0.2

class _App(tk.Tk):

    def __init__(self) -> None:
        super().__init__()
        self.init_tk()
        self.frame: Optional[tk.Frame] = None
        self.pos1_relative: Optional[Pos2] = None
        self.pos1_absolute: Optional[Pos2] = None
        self.pos2_absolute: Optional[Pos2] = None
        self.update_geometry()

    def init_tk(self) -> None:
        self.overrideredirect(True)
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

    def on_click(self, event) -> None: #grabs pos1 and initializes the frame
        self.pos1_relative = Pos2(event.x, event.y) #For tkinter
        self.pos1_absolute = Pos2(self.winfo_pointerx(), self.winfo_pointery()) #For screenshot

    def on_move(self, event) -> None: #updates the frame
        if not self.pos1_relative: return
        if self.frame:
            self.frame.destroy()
        pos: Pos2 = Pos2(event.x, event.y)
        diff: Pos2 = self.pos1_relative-pos
        self.frame = tk.Frame(master=self, width=abs(diff.x), height=abs(diff.y), bg="black")
        self.frame.place(x=self.pos1_relative[0] if diff.x < 0 else self.pos1_relative.x - diff.x,
                         y=self.pos1_relative[1] if diff.y < 0 else self.pos1_relative[1] - diff.y)

    def on_release(self, _) -> None: #grabs pos2 and destroys the _App
        self.pos2_absolute = Pos2(self.winfo_pointerx(), self.winfo_pointery())
        self.exit()

    def exit(self) -> None:
        if self.cancel_update_id:
            try:
                self.after_cancel(self.cancel_update_id)
            except Exception as e:
                print(e)
        self.destroy()

    def update_geometry(self): #Checks which monitor the cursor is on
        self.focus_set()
        self.focus_force()
        monitor: Monitor = MonitorHandler.find_new_monitor(Pos2(self.winfo_pointerx(), self.winfo_pointery()))
        self.geometry('{}x{}+{}+{}'.format(str(monitor.width), str(monitor.height), str(monitor.x), str(monitor.y)))
        self.cancel_update_id = self.after(5, self.update_geometry)

def _run_tkinter() -> tuple[Optional[Pos2], Optional[Pos2]]: #Initialises tkinter loop and starts the loop. Returns pos1 and pos2
    app: _App = _App()
    app.bind('<Escape>', app.exit)
    app.mainloop()
    return app.pos1_absolute, app.pos2_absolute

def _sort_coords(pos_tuple):
    coordinates = map(sorted, zip(*pos_tuple))
    return (Pos2(*l) for l in zip(*coordinates))

def grab() -> Optional[Image]:
    try:
        pos1, pos2 = _sort_coords(_run_tkinter())
        image = getRectAsImage((*pos1, *pos2)).convert('L') # BUG, breaks with Window's content scaling
        #image.show() # For debugging
        return image # in PIL format
    except:
        return None
