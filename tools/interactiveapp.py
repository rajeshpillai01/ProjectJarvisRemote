import time

import pyautogui
from pydantic import BaseModel, Field
import time
import pygetwindow as gw

class InteractAppArgs(BaseModel):
    window_title: str = Field(
        description="The exact title of the active window to focus (e.g., 'Calculator', 'Notepad')."
    )
    keys_to_type: str = Field(
        description="The math equation or text to type. Translate words to symbols (e.g., 'add 5 and 5' must be '5+5enter'). Always end with 'enter' to execute."
    )



def interact_with_active_app(window_title: str, keys_to_type: str) -> str:
    """Finds an open window, brings it to front, and inputs keys."""
    try:
        if window_title.lower() in ["calc", "calculator"]:
            window_title = "Calculator"
        elif window_title.lower() in ["notepad", "note"]:
            window_title = "Notepad"

        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            return f"I couldn't find an open window titled '{window_title}', sir. Is it running?"

        app_window = windows[0]
        if app_window.isMinimized:
            app_window.restore()

        app_window.activate()
        time.sleep(0.5)

        if keys_to_type.endswith("enter"):
            clean_keys = keys_to_type.replace("enter", "")
            pyautogui.write(clean_keys, interval=0.05)
            pyautogui.press('enter')
        else:
            pyautogui.write(keys_to_type, interval=0.05)

        return f"Successfully entered data into '{window_title}'."
    except Exception as e:
        return f"Failed to interact: {str(e)}"

