import pyperclip

import hotkey_listener
from graphics import grab
from analyze import analyze

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