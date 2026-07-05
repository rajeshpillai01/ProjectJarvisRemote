import os
import webbrowser


def open_website_or_app(target: str) -> str:
    """Opens a specified website URL or standard Windows application/executable."""
    if target.startswith("http://") or target.startswith("https://") or ".com" in target:
        webbrowser.open(target)
        return f"Successfully opened website: {target}"
    else:
        os.system(f"start {target}")
        return f"Fired command to launch application: {target}"