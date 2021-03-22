import pyperclip

from src.analyze import analyze
from src.graphics import grab
import src.hotkey_listener as hotkey_listener

def main():
    while True:
        hotkey_listener.listen()
        
        image = grab()

        if image is None: continue

        output = analyze(image)
        
        print(f"Output: {output}")
        if output:
            pyperclip.copy(output)

if __name__ == '__main__':
    main()