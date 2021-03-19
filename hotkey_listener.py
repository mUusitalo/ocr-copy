from pynput import keyboard as kb
import os
    
def listen():
    with kb.GlobalHotKeys({
        '<alt>+s': lambda: kb.Listener.stop(listener), # Stop listener
        '<shift>+<esc>': lambda: os._exit(0) # Kill program
    }) as listener:
        listener.join()
    return