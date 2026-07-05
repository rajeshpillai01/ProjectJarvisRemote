import os
import logging
import pyautogui
import webbrowser
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
TELEGRAM_TOKEN = "8957494842:AAGLTkj1uj5KaDb8CZV2rSTMCxzGJ1Tbe7E"
ALLOWED_USER_ID = 8889740442
GEMINI_API_KEY = "AIzaSyBCX2utYLCu5hB4JOPytyUma820GOSIsJU"  # Keep your key here
# ────────────────────────────────────────────────────────────────────────────

ai_client = genai.Client(api_key=GEMINI_API_KEY)

# We are expanding Jarvis's action vocabulary here
JARVIS_SYSTEM_INSTRUCTION = """
You are Jarvis, a highly sophisticated, polite AI assistant controlling the user's Windows PC.
The user is commanding you remotely via text.

Analyze the user's intent and choose ONE of the following actions to prefix your response with:
- [ACTION: SCREENSHOT] -> If they want to see what's on their screen or check status.
- [ACTION: LOCK] -> If they want to lock the PC.
- [ACTION: UNLOCK] -> If they want to unlock the PC.
- [ACTION: URL|website_address] -> If they want to open a website. Example: [ACTION: URL|https://youtube.com]
- [ACTION: APP|app_name] -> If they want to open a standard windows app. Example: [ACTION: APP|notepad] or [ACTION: APP|calc]
- [ACTION: TEXT] -> For general chatting or answering questions.

Format your response exactly like this:
[ACTION: CHOSEN_ACTION]
Your conversational response to the user here, addressing them politely as 'Sir'.
"""


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ALLOWED_USER_ID:
        return

    user_text = update.message.text
    logging.info(f"Jarvis received: {user_text}")

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=JARVIS_SYSTEM_INSTRUCTION,
                temperature=0.3,
            )
        )

        ai_reply = response.text

        # ─── ACTION PARSING ──────────────────────────────────────────────────
        if "[ACTION: SCREENSHOT]" in ai_reply:
            clean_reply = ai_reply.replace("[ACTION: SCREENSHOT]", "").strip()
            await update.message.reply_text(clean_reply if clean_reply else "Right away, sir.")

            screenshot_path = "screenshot.png"
            pyautogui.screenshot(screenshot_path)
            with open(screenshot_path, 'rb') as photo:
                await update.message.reply_photo(photo=photo)
            os.remove(screenshot_path)

        elif "[ACTION: LOCK]" in ai_reply:
            clean_reply = ai_reply.replace("[ACTION: LOCK]", "").strip()
            await update.message.reply_text(clean_reply)
            os.system('rundll32.exe user32.dll,LockWorkStation')

        elif "[ACTION: URL|" in ai_reply:
            # Extract URL: e.g., "[ACTION: URL|https://google.com]" -> "https://google.com"
            parts = ai_reply.split("]")
            action_part = parts[0]
            clean_reply = parts[1].strip()

            url = action_part.split("|")[1]
            await update.message.reply_text(clean_reply)
            webbrowser.open(url)

        elif "[ACTION: APP|" in ai_reply:
            parts = ai_reply.split("]")
            action_part = parts[0]
            clean_reply = parts[1].strip()

            app_name = action_part.split("|")[1]
            await update.message.reply_text(clean_reply)
            os.system(f"start {app_name}")  # Windows start command

        else:
            clean_reply = ai_reply.replace("[ACTION: TEXT]", "").strip()
            await update.message.reply_text(clean_reply)

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")


def main():
    print("Jarvis is online and fully upgraded...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == '__main__':
    main()