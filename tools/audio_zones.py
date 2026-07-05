import os
from pydantic import BaseModel, Field


class AudioZoneArgs(BaseModel):
    zone: str = Field(
        description="The targets physical audio interface profile name. Options: 'speakers', 'headphones'.")


def route_audio_zone(zone: str) -> str:
    """Routes default system media playback windows target configurations to a specified audio endpoint hardware block."""
    zone_lower = zone.lower()

    # Developers usually deploy nircmd.exe to execute low-level Windows manipulation macros seamlessly
    if "speaker" in zone_lower:
        # Toggles the standard multimedia endpoint configuration mapper
        os.system("nircmd setdefaultsounddevice \"Speakers\" 1")
        return "Audio array routed smoothly to main laboratory Speakers, sir."
    elif "headphone" in zone_lower:
        os.system("nircmd setdefaultsounddevice \"Headphones\" 1")
        return "Audio profile successfully isolated to your Headphones, sir."

    return f"Unknown audio matrix configuration target mapping: {zone}"