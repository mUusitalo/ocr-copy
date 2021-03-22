from copy import copy
import functools
import json
import pathlib
import re
from typing import Callable, Iterator

import pytesseract as tess
from pynput import keyboard as kb

print = functools.partial(print, flush=True)

class InputError(Exception):
    """Class that indicates bad user inputs"""
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
    
class SettingValidityTester:
    """Class containing only static methods for testing setting validity"""
    @staticmethod
    def hotkey(hotkey: str) -> str:
        """Try to parse hotkey to raise an InputError if it's invalid."""
        try:
            kb.HotKey.parse(hotkey)
            return hotkey
        except:
            raise InputError(f"Invalid hotkey: {hotkey}")

    @staticmethod
    def tesseract_path(path: str) -> str:
        """Set pytesseract's path to tesseract.exe.
        Try to get version number to raise an exception if the path is invalid.
        Raise InputError when an invalid path is entered.
        """
        path = str(pathlib.Path(path))
        tess.pytesseract.tesseract_cmd = path
        try:
            print(f"Tesseract version: {tess.get_tesseract_version()}") # Will throw error if path is invalid
        except:
            raise InputError("Invalid path to tesseract.exe. Running the program now will produce an error.")
        return path

    @staticmethod
    def languages(input_languages: str) -> str:
        """Parse languages using regex.
        Check that they're all in the available languages.
        Throw InputError if an invalid string is entered.
        """
        lang_list: list[str] = re.findall(r'(?i)[\w_]+', input_languages)
        available_languages: set[str] = get_available_languages()
        for lang in lang_list:
            if not lang.lower() in available_languages:
                raise InputError(f"Unexpected input: {lang}")
        return '+'.join(lang_list).lower()

class Settings:
    """Class for storing setting and generating them from user input.
    Also contains methods for reading and writing settings to and from .json.
    Uses SettingsValidityTester for testing inputs.
    """
    # Dict containing each setting and the method for testing it's input value.
    value_test_map = {
        'capture_hotkey': SettingValidityTester.hotkey,
        'exit_hotkey': SettingValidityTester.hotkey,
        'tesseract_path': SettingValidityTester.tesseract_path,
        'languages': SettingValidityTester.languages
    }

    def __init__(self,
                 capture_hotkey:str='', exit_hotkey:str='',
                 tesseract_path:str='', languages:str=''):
        self.capture_hotkey: str = capture_hotkey
        self.exit_hotkey: str = exit_hotkey
        self.tesseract_path: str = tesseract_path
        self.languages: str = languages

    @staticmethod
    def from_file() -> 'Settings':
        """Generate Settings object from .json file"""
        try:
            with open(SETTINGS_PATH, 'r') as settings_file:
                return Settings(**json.loads(settings_file.read()))
        except:
            print("Settings file is missing or corrupted.")
            try: # try-except here in case DEFAULT_SETTINGS doesn't exist
                return copy(DEFAULT_SETTINGS)
            except:
                return Settings()

    def to_file(self) -> None:
        """Write Settings object to file"""
        with open(SETTINGS_PATH, 'w') as settings_file:
            settings_file.write(json.dumps(dict(self)))

    def __iter__(self) -> Iterator[tuple[str, str]]:
        """Yield tuple with attribute name and value for each name in value_test_map."""
        for setting in self.value_test_map.keys():
            yield setting, getattr(self, setting)

    def __str__(self):
        """Generate user-readable string containing all settings and their values."""
        return '\n'.join(f"    {setting}: {value or '-'}" for setting, value in self)

    def _try_setattr(self, name: str, value: str, callback: Callable = None) -> None:
        """Test input value and set it if it's valid.
        Call 'callback' if an InputError is caught.
        """
        try:
            if value:
                value = self.value_test_map[name](value) 
            setattr(self, name, value)
        except InputError as e:
            print(e)
            if callback: callback()

    def _prompt_setting(self, setting: str) -> None:
        """Ask the user to input a certain setting's value.
        Call function again if the value is invalid but don't do anything if the input is blank.
        """
        print(f"\nCurrent {setting}: {getattr(self, setting) or '-'}")
        output: str = input(f"Enter {setting}: ")
        if not output: return # Setting skipped
        self._try_setattr(setting, output.strip(), lambda: self._prompt_setting(setting))

    def _reset_defaults(self) -> None:
        """Reset default settings. If DEFAULT_SETTINGS doesn't exist, use a blank Settings object."""
        try:
            new_settings: Settings = DEFAULT_SETTINGS
        except:
            new_settings: Settings = Settings()
        for key, value in new_settings:
            self._try_setattr(key, value)
            
    def _prompt_reset(self) -> None:
        """Ask the user whether they want to reset the values.
        If yes, then copy the default settings.
        """
        reset: str = input("Restore defaults? (y/N):")
        if reset == 'y':
            self._reset_defaults()
            print(f"\nCurrent settings:\n{str(self)}\n")
            
    def run_dialog(self) -> 'Settings':
        """Run dialog for entering settings.
        First ask the user whether to reset the values.
        Then ask to input each setting.
        Leaving a setting blank will skip, entering spaces will clear.
        Entering an invalid setting will let the user try again.
        """
        print(f"\nCurrent settings:\n{str(self)}\n")
        self._prompt_reset()
        print("Enter settings. Leave blank to skip and enter one space to clear.")
        for setting, _ in self:
            self._prompt_setting(setting)
        print(f"\nCurrent settings:\n{str(self)}\n")
        return self

DEFAULT_SETTINGS: Settings = Settings(
    tesseract_path=str(pathlib.Path('C:/Program Files/Tesseract-OCR/tesseract.exe')),
    exit_hotkey='<shift>+<esc>',
    capture_hotkey='<alt>+s',
    languages='eng'
)

settings: Settings = Settings.from_file()

if __name__ == '__main__':
    settings.run_dialog().to_file()
