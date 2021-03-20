import json
import pathlib
import re

import pytesseract as tess
from pynput import keyboard as kb

SETTINGS_PATH = './settings.json'

# Default settings
TESSERACT_PATH = str(pathlib.Path('C:/Program Files/Tesseract-OCR/tesseract.exe'))
EXIT_HOTKEY = '<shift>+<esc>'
CAPTURE_HOTKEY = '<alt>+s'
LANGUAGES = 'eng'

# Available languages are listed here because pytesseract.get_languages() requires a valid path to tesseract.exe
AVAILABLE_LANGUAGES = {
    'afr', 'amh', 'ara', 'asm', 'aze', 'aze_cyrl', 'bel', 'ben', 'bod',
    'bos', 'bre', 'bul', 'cat', 'ceb', 'ces', 'chi_sim', 'chi_sim_vert',
    'chi_tra', 'chi_tra_vert', 'chr', 'cos', 'cym', 'dan', 'deu', 'div',
    'dzo', 'ell', 'eng', 'enm', 'epo', 'equ', 'est', 'eus', 'fao', 'fas',
    'fil', 'fin', 'fra', 'frk', 'frm', 'fry', 'gla', 'gle', 'glg', 'grc',
    'guj', 'hat', 'heb', 'hin', 'hrv', 'hun', 'hye', 'iku', 'ind', 'isl',
    'ita', 'ita_old', 'jav', 'jpn', 'jpn_vert', 'kan', 'kat', 'kat_old',
    'kaz', 'khm', 'kir', 'kmr', 'kor', 'lao', 'lat', 'lav', 'lit', 'ltz',
    'mal', 'mar', 'mkd', 'mlt', 'mon', 'mri', 'msa', 'mya', 'nep', 'nld',
    'nor', 'oci', 'ori', 'pan', 'pol', 'por', 'pus', 'que', 'ron', 'rus',
    'san', 'sin', 'slk', 'slv', 'snd', 'spa', 'spa_old', 'sqi', 'srp',
    'srp_latn', 'sun', 'swa', 'swe', 'syr', 'tam', 'tat', 'tel', 'tgk',
    'tha', 'tir', 'ton', 'tur', 'uig', 'ukr', 'urd', 'uzb', 'uzb_cyrl',
    'vie', 'yid', 'yor'}

class Settings:
    """
    Singleton class for storing, reading, and writing settings. All settings have getters and setters that make sure the settings are valid.
    Will throw errors if settings are invalid.
    """

    _instance = None

    def __new__(cls):
        cls._instance = cls._instance or super().__new__(cls)._init()
        return cls._instance
            
    def _init(self):
        try:
            self._read()
        except Exception as e:
            print(e)
            self._reset()
        return self

    def __dir__(self):
        return ['capture_hotkey', 'exit_hotkey', 'tesseract_path', 'languages']

    def __iter__(self):
        for attr in dir(self):
            yield attr, getattr(self, attr, '')

    def __str__(self):
        return '\n'.join(f"    {setting}: {value or '-'}" for setting, value in self)

    @staticmethod
    def test_hotkey(hotkey: str) -> None:
        kb.HotKey.parse(hotkey)
        return hotkey

    def _prompt(self, attribute: str) -> str:
        print(f"\nCurrent {attribute}: {getattr(self, attribute, None)}")
        output = input(f"Enter {attribute}: ")
        if not output: return # Setting skipped
        try:
            setattr(self, attribute, output.strip())
        except Exception as e:
            print(e)
            self._prompt(attribute)

    def _reset(self):
        try: self.tesseract_path = TESSERACT_PATH
        except: self.tesseract_path = None

        try: self.languages = LANGUAGES
        except: self.languages = None
        
        try: self.exit_hotkey = EXIT_HOTKEY
        except: self.exit_hotkey = None
        
        try: self.capture_hotkey = CAPTURE_HOTKEY
        except: self.capture_hotkey = None

    def _dialog(self):
        print(f"\nCurrent settings:\n{str(self)}\n")
        reset = input("Restore defaults? (y/N):")
        if reset == 'y':
            self._reset()
            print(f"\nCurrent settings:\n{str(self)}\n")
        print("Enter settings. Leave blank to skip and enter one space to clear.")

        for attribute in (attribute for attribute in dir(self) if not attribute.startswith('_')):
            self._prompt(attribute)
        print(f"\nCurrent settings:\n{str(self)}\n")
        return self

    def _read(self) -> 'Settings':
        with open(SETTINGS_PATH, 'r') as settings_file:
            settings_dict = json.loads(settings_file.read())
        sorted_settings_dict = dict(sorted(settings_dict.items(), key=lambda item: dir(self).index(item[0]))) # This is broken: dir() apparently sorts alphabetically.
        for key, value in sorted_settings_dict.items():
            if key in dir(self):
                try:
                    setattr(self, key, value)
                except:
                    setattr(self, key, None)

    def _write(self):
        settings_dict = {attr: getattr(self, attr, None) for attr in dir(self)}
        with open(SETTINGS_PATH, 'w') as settings_file:
            settings_file.write(json.dumps(settings_dict))

    @property
    def tesseract_path(self) -> str:
        return getattr(self, '_tesseract_path', '')

    @tesseract_path.setter
    def tesseract_path(self, input_path: str) -> None:
        if not input_path:
            self._tesseract_path = ''
        else:
            path = str(pathlib.Path(input_path))
            tess.pytesseract.tesseract_cmd = path
            print(f"Tesseract version: {tess.get_tesseract_version()}") # Will throw error if path is invalid
            self._tesseract_path = path
    
    @property
    def languages(self) -> str:
        return getattr(self, '_languages', '')

    @languages.setter
    def languages(self, input_languages: str) -> None:
        input_languages = input_languages or '' # Change None to str
        lang_list = re.findall(r'(?i)[\w_]+', input_languages)
        try:
            # Will throw an exception if self._tesseract_path is invalid
            available_languages = set(tess.get_languages())
        except:
            available_languages = AVAILABLE_LANGUAGES
        for lang in lang_list:
            if not lang.lower() in available_languages:
                raise ValueError(f"Unexpected input: {lang}")
        self._languages = '+'.join(lang_list).lower()

    @property
    def exit_hotkey(self) -> str:
        return getattr(self, '_exit_hotkey', '')
    
    @exit_hotkey.setter
    def exit_hotkey(self, hotkey: str) -> None:
        self._exit_hotkey = self.test_hotkey(hotkey) if hotkey else ''

    @property
    def capture_hotkey(self) -> str:
        return getattr(self, '_capture_hotkey', '')

    @capture_hotkey.setter
    def capture_hotkey(self, hotkey: str) -> None:
        self._capture_hotkey = self.test_hotkey(hotkey) if hotkey else ''

Settings() # Create singleton to intialize it

if __name__ == '__main__':
    Settings()._dialog()._write()
