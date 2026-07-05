import pyautogui
from pydantic import BaseModel, Field

class HotkeyArgs(BaseModel):
    combination: str = Field(description="Comma-separated keys to press together. Example: 'ctrl,alt,delete' or 'win,d'.")

def trigger_global_hotkey(combination: str) -> str:
    """Simulates a physical global shortcut chord press configuration on the host computer environment."""
    try:
        keys = [k.strip().lower() for k in combination.split(",")]
        # Execute key down events in sequence
        for key in keys:
            pyautogui.keyDown(key)
        # Release them in reverse order
        for key in reversed(keys):
            pyautogui.keyUp(key)
        return f"Successfully executed macro shortcut layout: {combination}"
    except Exception as e:
        return f"Hotkey subsystem execution exception: {str(e)}"