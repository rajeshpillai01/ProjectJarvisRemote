import os
import logging
import pyautogui
import webbrowser
import ctypes
from PIL import Image
import google.genai as genai
from google.genai import types
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from pydantic import BaseModel, Field


from dotenv import load_dotenv

from tools.audio import set_system_volume
from tools.interactiveapp import interact_with_active_app, InteractAppArgs
from tools.lockworkstation import lock_workstation
from tools.openwebsiteorapp import open_website_or_app
from tools.runterminalcommand import run_terminal_command
from tools.screenshot import take_screenshot, EmptyArgs

load_dotenv() # This automatically injects your .env file into os.environ

import config # Now you can safely import your config module!



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
#TELEGRAM_TOKEN = "8957494842:AAGLTkj1uj5KaDb8CZV2rSTMCxzGJ1Tbe7E"
#ALLOWED_USER_ID = 8889740442
#GEMINI_API_KEY = "AIzaSyBCX2utYLCu5hB4JOPytyUma820GOSIsJU"
# ────────────────────────────────────────────────────────────────────────────

ai_client = genai.Client(api_key=config.GEMINI_API_KEY)


# ─── PYDANTIC TOOL SCHEMAS ──────────────────────────────────────────────────

class OpenAppArgs(BaseModel):
    target: str = Field(
        description="The precise Windows executable name (e.g., 'calc', 'notepad') or a web URL."
    )






# ─── JARVIS'S PHYSICAL TOOLS (SYNCHRONOUS ONLY) ──────────────────────────────

#def set_system_volume(level: int) -> str:
#    """Sets the master system volume to a percentage between 0 and 100."""
#    level = max(0, min(100, level))
#    return f"Adjusting system volume toward {level}%"





# System Function Registry Map
tools_map = {
    "open_website_or_app": open_website_or_app,
    "set_system_volume": set_system_volume,
    "lock_workstation": lock_workstation,
    "run_terminal_command": run_terminal_command,
    "interact_with_active_app": interact_with_active_app,
    "take_screenshot": take_screenshot
}

# ─── SYSTEM INSTRUCTIONS ─────────────────────────────────────────────────────
JARVIS_INSTRUCTION = (
    "You are Jarvis, an advanced remote execution agent for a Windows PC.\n"
    "Your primary job is to select the single most appropriate tool based on strict boundary definitions:\n"
    "1. To launch a brand new program or URL, use 'open_website_or_app'.\n"
    "2. To type or enter data into an active window, use 'interact_with_active_app'.\n"
    "3. If the user explicitly asks for an image/screenshot of their desktop without further questions, invoke 'take_screenshot'."
)


# ─── CORE TELEGRAM & AI LOGIC ────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != config.ALLOWED_USER_ID:
        return

    user_text = update.message.text
    logging.info(f"Jarvis received next-gen request: {user_text}")

    # Vision Subsystem Triggers (Multimodal interpretation)
    if any(phrase in user_text.lower() for phrase in ["look at my screen", "what am i doing", "see this"]):
        await update.message.reply_text("Scanning your monitors now, sir...")
        screenshot_path = "jarvis_vision.png"
        pyautogui.screenshot(screenshot_path)

        img = Image.open(screenshot_path)
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[img,
                      f"The user is asking: '{user_text}'. Describe what is on their screen clearly. Be polite and address them as sir."]
        )
        await update.message.reply_text(response.text)
        os.remove(screenshot_path)
        return

    # Standard tool execution request pipeline
    try:
        open_tool = types.FunctionDeclaration(
            name="open_website_or_app",
            description="ONLY use to launch a BRAND NEW application or website that is not currently running.",
            parameters=OpenAppArgs
        )

        interact_tool = types.FunctionDeclaration(
            name="interact_with_active_app",
            description="ONLY use to type, calculate, or enter text into an application window that is ALREADY OPEN on screen.",
            parameters=InteractAppArgs
        )

        # Fixed: Uses EmptyArgs schema so Gemini knows it doesn't need parameters
        screenshot_tool = types.FunctionDeclaration(
            name="take_screenshot",
            description="ONLY use when the user directly wants to capture, snap, or take a screenshot of the system screen.",
            parameters=EmptyArgs
        )

        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=JARVIS_INSTRUCTION,
                # Fixed: Properly passed the screenshot_tool blueprint to the tool array
                tools=[types.Tool(function_declarations=[open_tool, interact_tool, screenshot_tool])],
                temperature=0.0,
                automatic_function_calling={"disable": True}
            )
        )

        if response.function_calls:
            for call in response.function_calls:
                func_name = call.name
                func_args = call.args

                logging.info(f"Gemini invoked tool strictly: {func_name} with args: {func_args}")
                await update.message.reply_text(f"Jarvis: Accessing tool subsystem '{func_name}'...")

                if func_name in tools_map:
                    # Run the synchronous function safely
                    execution_result = tools_map[func_name](**func_args)

                    # Intercept screenshot marker response to handoff to the Telegram client safely
                    if execution_result == "__SEND_SCREENSHOT_MARKER__":
                        with open("screenshot.png", 'rb') as photo:
                            await update.message.reply_photo(photo=photo, caption="Here is the capture, sir.")
                        os.remove("screenshot.png")
                    else:
                        await update.message.reply_text(execution_result)
                else:
                    await update.message.reply_text("Tool mapped incorrectly in systems registry.")
        else:
            await update.message.reply_text(response.text)

    except Exception as e:
        await update.message.reply_text(f"System Exception: {str(e)}")


def main():
    print("Jarvis 2.0 is online. Next-gen tool routing active...")
    app = Application.builder().token(config.TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == '__main__':
    main()