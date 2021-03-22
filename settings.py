from copy import copy
import functools
import json
import pathlib
import re

import pytesseract as tess
from pynput import keyboard as kb

print = functools.partial(print, flush=True)

class InputError(Exception):
    pass

SETTINGS_PATH: str = 'settings.json'

# Available languages are listed here because pytesseract.get_languages() requires a valid path to tesseract.exe
AVAILABLE_LANGUAGES: set[str] = {
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

def get_available_languages() -> set[str]:
    try:
        # Will throw an exception if tesseract_cmd is invalid
        return set(tess.get_languages())
    except EnvironmentError:
        return AVAILABLE_LANGUAGES

def test_hotkey(hotkey: str = ''):
    if not hotkey: return hotkey
    try:
        kb.HotKey.parse(hotkey)
        return hotkey
    except:
        raise InputError(f"Invalid key: {hotkey}")

class Settings:

    all_settings = ['capture_hotkey', 'exit_hotkey', 'tesseract_path', 'languages']


    def __init__(self, 
                 capture_hotkey: str='', exit_hotkey: str='',
                 tesseract_path: str='', languages: str='', verbose=True):
        self._verbose: bool = verbose
        self.capture_hotkey: str = capture_hotkey
        self.exit_hotkey: str = exit_hotkey
        self.tesseract_path: str = tesseract_path
        self.languages: str = languages

    def __iter__(self):
        for setting in self.all_settings:
            yield setting, getattr(self, setting)

    def __str__(self):
        return '\n'.join(f"    {setting}: {value or '-'}" for setting, value in self)

    @staticmethod
    def from_dict(settings_dict) -> 'Settings':
        settings = Settings()
        for key, value in settings_dict.items():
            if key in Settings.all_settings:
                try:
                    setattr(settings, key, value)
                except InputError:
                    pass
        return settings

    @staticmethod
    def from_file() -> 'Settings':
        try:
            with open(SETTINGS_PATH, 'r') as settings_file:
                settings_dict = json.loads(settings_file.read())
            return Settings.from_dict(settings_dict)
        except:
            print("Settings file is missing or corrupted.")
            return copy(DEFAULT_SETTINGS)

    @staticmethod
    def to_file(settings: 'Settings'):
        settings_dict = {setting: value for setting, value in settings}
        with open(SETTINGS_PATH, 'w') as settings_file:
            settings_file.write(json.dumps(settings_dict))

    def _prompt_setting(self, setting: str):
        print(f"\nCurrent {setting}: {getattr(self, setting) or '-'}")
        output = input(f"Enter {setting}: ")
        if not output: return # Setting skipped
        try:
            setattr(self, setting, output.strip())
        except InputError as e:
            print(e)
            self._prompt_setting(setting)

    def _prompt_reset(self) -> None:
        reset = input("Restore defaults? (y/N):")
        if reset == 'y':
            for key, value in DEFAULT_SETTINGS:
                try:
                    setattr(self, key, value)
                except InputError:
                    pass
            print(f"\nCurrent settings:\n{str(self)}\n")
            
    def run_dialog(self) -> None:
        print(f"\nCurrent settings:\n{str(self)}\n")
        self._prompt_reset()
        print("Enter settings. Leave blank to skip and enter one space to clear.")
        for setting, _ in self:
            self._prompt_setting(setting)
        print(f"\nCurrent settings:\n{str(self)}\n")

    @property
    def tesseract_path(self) -> str:
        return self._tesseract_path

    def _warn_no_connection(self) -> None:
        if not self._verbose: return
        print("The current path to tesseract.exe is invalid. Running the program now will produce a runtime error.")

    @tesseract_path.setter
    def tesseract_path(self, input_path: str) -> None:
        if not input_path:
            self._tesseract_path = ''
            self._warn_no_connection()
        else:
            path = str(pathlib.Path(input_path))
            tess.pytesseract.tesseract_cmd = path
            try:
                tesseract_version = tess.get_tesseract_version() # Will throw error if path is invalid
            except EnvironmentError as e:
                raise InputError(str(e))
            if self._verbose:
                print(f"Tesseract version: {tesseract_version}")
            self._tesseract_path: str = path
    
    @property
    def languages(self) -> str:
        return self._languages

    @languages.setter
    def languages(self, input_languages: str) -> None:
        lang_list: list[str] = re.findall(r'(?i)[\w_]+', input_languages)
        available_languages: set[str] = get_available_languages()
        for lang in lang_list:
            if not lang.lower() in available_languages:
                raise InputError(f"Unexpected input: {lang}")
        self._languages: str = '+'.join(lang_list).lower()

    @property
    def exit_hotkey(self) -> str:
        return self._exit_hotkey
    
    @exit_hotkey.setter
    def exit_hotkey(self, hotkey: str) -> None:
        self._exit_hotkey: str = test_hotkey(hotkey)

    @property
    def capture_hotkey(self) -> str:
        return self._capture_hotkey

    @capture_hotkey.setter
    def capture_hotkey(self, hotkey: str) -> None:
        self._capture_hotkey: str = test_hotkey(hotkey)

DEFAULT_SETTINGS: Settings = Settings(
    tesseract_path=str(pathlib.Path('C:/Program Files/Tesseract-OCR/tesseract.exe')),
    exit_hotkey='<shift>+<esc>',
    capture_hotkey='<alt>+s',
    languages='eng',
    verbose=False
)

settings = Settings().from_file()

if __name__ == '__main__':
    settings.run_dialog()
    Settings.to_file(settings)
