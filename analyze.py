import pytesseract as tess
from pyzbar import pyzbar
from settings import Settings

def analyze(image):
    data = pyzbar.decode(image)
    if data:
        return data[0].data.decode()
    else:
        return tess.image_to_string(image, lang=Settings().languages)