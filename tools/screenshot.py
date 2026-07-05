from pydantic import BaseModel, Field
import pyautogui

class EmptyArgs(BaseModel):
    """Schema for tools that do not require input arguments."""
    pass

# Fixed: Removed 'async def' and 'update' dependency so it fits your standard function execution map cleanly.
# It saves the image file, and returns a marker path string so the async Telegram handler knows to upload it.
def take_screenshot() -> str:
    """Captures a full screenshot of the desktop environment."""
    screenshot_path = "screenshot.png"
    pyautogui.screenshot(screenshot_path)
    return "__SEND_SCREENSHOT_MARKER__"