import pytesseract as tess
from pyzbar import pyzbar
from settings import settings

def analyze(image) -> str:
    data: list[pyzbar.Decoded] = pyzbar.decode(image)
    if data:
        return data[0].data.decode()
    else:
        return tess.image_to_string(image, lang=settings.languages).strip()