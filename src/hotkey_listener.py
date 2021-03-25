from pynput import keyboard as kb
import os

from settings import settings

def listen() -> None:
    with kb.GlobalHotKeys({
        settings.capture_hotkey: lambda: kb.Listener.stop(listener), # Stop listener
        settings.exit_hotkey: lambda: os._exit(0) # Kill program
    }) as listener:
        listener.join()
    return