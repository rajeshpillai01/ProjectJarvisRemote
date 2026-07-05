import ctypes


def lock_workstation() -> str:
    """Instantly locks the Windows computer desktop."""
    ctypes.windll.user32.LockWorkStation()
    return "The workstation has been securely locked, sir."