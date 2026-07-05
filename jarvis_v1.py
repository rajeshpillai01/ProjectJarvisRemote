import os
import logging
import pyautogui
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging to see errors in the terminal
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
# Paste your Telegram Bot Token here
TELEGRAM_TOKEN = "8957494842:AAGLTkj1uj5KaDb8CZV2rSTMCxzGJ1Tbe7E"

# YOUR TELEGRAM USER ID: To find this, message @userinfobot on Telegram.
# This ensures ONLY you can command Jarvis.
ALLOWED_USER_ID = 8889740442  # Replace with your actual ID (integer, no quotes)


# ────────────────────────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Security Gatekeeper
    if user_id != ALLOWED_USER_ID:
        logging.warning(f"Unauthorized access attempt by user ID: {user_id}")
        return

    command_text = update.message.text.lower()
    await update.message.reply_text(f"Jarvis: Processing command '{command_text}'...")

    try:
        # Basic Hardcoded Tools for testing the "hands"
        if "screenshot" in command_text:
            screenshot_path = "screenshot.png"
            pyautogui.screenshot(screenshot_path)

            with open(screenshot_path, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption="Here is your screen, sir.")
            os.remove(screenshot_path)

        elif "lock" in command_text:
            await update.message.reply_text("Locking the computer.")
            # Windows lock command (Mac/Linux will need different commands)
            os.system('rundll32.exe user32.dll,LockWorkStation')

        else:
            await update.message.reply_text("I understand the connection is live, but I don't have my AI brain yet!")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")


def main():
    print("Jarvis is waking up... Press Ctrl+C to shut down.")
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Listen for any text message
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling Telegram for messages
    app.run_polling()


if __name__ == '__main__':
    main()