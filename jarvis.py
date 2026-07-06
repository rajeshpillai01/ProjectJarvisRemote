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
from tools.email_sender import EmailArgs, send_background_email
from tools.interactiveapp import interact_with_active_app, InteractAppArgs
from tools.lockworkstation import lock_workstation
from tools.openwebsiteorapp import open_website_or_app
from tools.runterminalcommand import run_terminal_command
from tools.screenshot import take_screenshot, EmptyArgs

load_dotenv() # This automatically injects your .env file into os.environ

import config # Now you can safely import your config module!
from tools.memory import memorize_fact, recall_facts
from tools.voice import speak_out_loud
from tools.audio_zones import route_audio_zone
from pydantic import BaseModel, Field  # Ensure schemas match


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
    "take_screenshot": take_screenshot,
    "memorize_fact": memorize_fact,
    "recall_facts": recall_facts,
    "speak_out_loud": speak_out_loud,
    "route_audio_zone": route_audio_zone,
    "send_background_email": send_background_email
}

# ─── SYSTEM INSTRUCTIONS ─────────────────────────────────────────────────────
JARVIS_INSTRUCTION = (
    "You are Jarvis, an advanced remote execution agent for a Windows PC.\n"
    "Your primary job is to select the single most appropriate tool based on strict boundary definitions:\n"
    "1. To launch a brand new program or URL, use 'open_website_or_app'.\n"
    "2. To type or enter data into an active window, use 'interact_with_active_app'.\n"
    "3. To take a screenshot, use 'take_screenshot'.\n"
    "4. To save information, rules, or preferences about the user, use 'memorize_fact'.\n"
    "5. To search or recall things the user told you to remember, use 'recall_facts'.\n"
    "6. To vocalize speech physically through the computer's speakers, use 'speak_out_loud'.\n"
    "7. To change sound outputs between headphones and speakers, use 'route_audio_zone'.\n"
    "8. To send an email via gmail, use 'send_background_email'.\n"
)


# ─── CORE TELEGRAM & AI LOGIC ────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    class MemorizeArgs(BaseModel):
        fact: str = Field(description="Information to store.")

    class RecallArgs(BaseModel):
        query: str = Field(description="Topic to search memory for.")

    class SpeakArgs(BaseModel):
        phrase: str = Field(description="Text to say out loud.")

    class AudioZoneArgs(BaseModel):
        zone: str = Field(description="Target device group name.")


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
            parameters=OpenAppArgs.model_json_schema()
        )

        interact_tool = types.FunctionDeclaration(
            name="interact_with_active_app",
            description="ONLY use to type, calculate, or enter text into an application window that is ALREADY OPEN on screen.",
            parameters=InteractAppArgs.model_json_schema()
        )

        # Fixed: Uses EmptyArgs schema so Gemini knows it doesn't need parameters
        screenshot_tool = types.FunctionDeclaration(
            name="take_screenshot",
            description="ONLY use when the user directly wants to capture, snap, or take a screenshot of the system screen.",
            parameters=EmptyArgs.model_json_schema()
        )


        speak_tool = types.FunctionDeclaration(
            name="speak_out_loud",
            description="Use this tool when the user explicitly wants you to broadcast audio or say something out loud through the host computer's speakers.",
            parameters=SpeakArgs.model_json_schema()
        )

        zone_tool = types.FunctionDeclaration(
            name="route_audio_zone",
            description="Use this to change or route system sound output default devices between speakers and headphones.",
            parameters=AudioZoneArgs.model_json_schema()
        )

        # 2. Update the Tool declarations to explicitly convert your models
        memorize_tool = types.FunctionDeclaration(
            name="memorize_fact",
            description="Use this tool when the user explicitly instructs you to remember, save, or log a fact or preference.",
            # Explicitly force the Pydantic structure to pass its parameters dictionary representation
            parameters=MemorizeArgs.model_json_schema()
        )

        recall_tool = types.FunctionDeclaration(
            name="recall_facts",
            description="Use this tool when the user asks you what you remember about a topic or queries their logs.",
            parameters=RecallArgs.model_json_schema()
        )

        # Define the function blueprint declaration:
        email_tool = types.FunctionDeclaration(
            name="send_background_email",
            description="ONLY use when the user explicitly instructs you to send an email to a specific address with a subject or body text context.",
            parameters=EmailArgs.model_json_schema()
        )

        response = ai_client.models.generate_content(
            model='gemini-3.5-flash',
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=JARVIS_INSTRUCTION,
                # bundle ALL declarations into a single Tool object
                tools=[
                    types.Tool(
                        function_declarations=[
                            open_tool,
                            interact_tool,
                            screenshot_tool,
                            memorize_tool,
                            recall_tool,
                            speak_tool,
                            zone_tool,
                            email_tool
                        ]
                    )
                ],
                temperature=0.0,
                automatic_function_calling={"disable": True}
            )
        )

        if response.function_calls:
            for call in response.function_calls:
                func_name = call.name
                func_args = call.args

                logging.info(f"Gemini invoked tool strictly: {func_name} with args: {func_args}")
                print(f"DEBUG PAYLOAD FOR {func_name}: {type(func_args)} -> {func_args}")  # <-- Add this temporary line
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