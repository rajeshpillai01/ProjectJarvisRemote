import os
from pathlib import Path

# ─── PATH DEFINITIONS ────────────────────────────────────────────────────────
# Automatically finds the root directory of your project
BASE_DIR = Path(__file__).resolve().parent

# ─── SECURITY & AUTHENTICATION ───────────────────────────────────────────────
# Looks for environment variables on the host system.
# If they don't exist, it falls back to a message or fails gracefully.
TELEGRAM_TOKEN = os.environ.get("JARVIS_TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("JARVIS_GEMINI_API_KEY")

try:
    ALLOWED_USER_ID = int(os.environ.get("JARVIS_ALLOWED_USER_ID", "0"))
except ValueError:
    ALLOWED_USER_ID = 0


# ─── SYSTEM VALIDATION ───────────────────────────────────────────────────────
def validate_config():
    """Verifies that all required configuration variables are present at startup."""
    missing = []
    if not TELEGRAM_TOKEN:
        missing.append("JARVIS_TELEGRAM_TOKEN")
    if not GEMINI_API_KEY:
        missing.append("JARVIS_GEMINI_API_KEY")
    if not ALLOWED_USER_ID:
        missing.append("JARVIS_ALLOWED_USER_ID")

    if missing:
        raise ValueError(
            f"❌ Critical Configuration Error: Missing environment variables: {', '.join(missing)}.\n"
            f"Please set these variables in your system or environment configuration before launching Jarvis."
        )


# Run a quick check when imported to catch setup mistakes early
validate_config()