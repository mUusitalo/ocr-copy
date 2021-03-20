import pyperclip

from analyze import analyze
from graphics import grab
import hotkey_listener
import settings # Imported to initialize singleton

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