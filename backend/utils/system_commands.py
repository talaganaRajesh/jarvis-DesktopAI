import os
import subprocess
import pyautogui
import time
from typing import Dict, Callable

class SystemCommands:
    def __init__(self):
        self.commands: Dict[str, Callable] = {
            "open browser": self.open_browser,
            "take screenshot": self.take_screenshot,
            "minimize all": self.minimize_all,
            "maximize window": lambda: pyautogui.hotkey('win', 'up'),
            "minimize window": lambda: pyautogui.hotkey('win', 'down'),
            "next window": lambda: pyautogui.hotkey('alt', 'tab'),
            "volume up": lambda: pyautogui.press('volumeup'),
            "volume down": lambda: pyautogui.press('volumedown'),
            "mute": lambda: pyautogui.press('volumemute'),
        }

    def open_browser(self):
        if os.name == 'nt':
            subprocess.Popen(['start', 'chrome'], shell=True)
        else:
            subprocess.Popen(['google-chrome'])

    def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        screenshot.save(f"screenshot_{int(time.time())}.png")

    def minimize_all(self):
        if os.name == 'nt':
            pyautogui.hotkey('win', 'd')
        else:
            pyautogui.hotkey('command', 'm')

    def execute_command(self, command: str) -> bool:
        if command in self.commands:
            self.commands[command]()
            return True
        return False