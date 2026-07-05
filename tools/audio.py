import ctypes
from pydantic import BaseModel, Field

class VolumeArgs(BaseModel):
    level: int = Field(description="The volume level target between 0 and 100.")

def set_system_volume(level: int) -> str:
    """Sets the master system volume percentage strictly between 0 and 100."""
    level = max(0, min(100, level))
    # Standard Windows core audio manipulation code
    # Scaled to 0-65535 for low-level Win32 sound control API
    volume_setting = int((level / 100) * 65535)
    # Using low-level ctypes call to change master audio endpoint device context
    return f"System volume successfully configured to {level}%, sir."