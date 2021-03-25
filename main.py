import pyperclip
from typing import NoReturn, Union

from src.analyze import analyze
from src.graphics import grab
import src.hotkey_listener as hotkey_listener
from PIL.Image import Image

def main() -> NoReturn:
    while True:
        hotkey_listener.listen()
        
        image: Union[Image, None] = grab()

        if image is None: continue

        output: str = analyze(image)
        
        print(f"Output: {output}")
        if output:
            pyperclip.copy(output)

if __name__ == '__main__':
    main()