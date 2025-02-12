import os
import logging
import json

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext

from grocery_ocr import extract_and_save_data  # Import from your module
from grocery_sheets import write_to_sheet

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Telegram Bot Token (from BotFather)
# BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
BOT_TOKEN_FILE = "telegram_bot_token.txt"

# Load Telegram Bot Token from secret file
try:
    with open(BOT_TOKEN_FILE, "r") as f:
        BOT_TOKEN = f.read().strip()
except FileNotFoundError:
    logger.error(f"Telegram bot token file not found: {BOT_TOKEN_FILE}")
    exit(1)
except Exception as e:
    logger.error(f"Error reading Telegram bot token from file: {e}")
    exit(1)

if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable not set.")
    exit(1)

# Global variable to store the JSON data (you might want to improve this later)
extracted_data = None

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome to the Grocery Tracker Bot! Send me a photo of your receipt.")

async def process_receipt(update: Update, context: CallbackContext):
    user = update.effective_user
    photo_file = await update.message.photo[-1].get_file()  # Get the largest resolution photo
    await update.message.reply_text("Processing your receipt...")

    # Download the image to a temporary file
    temp_filename = f"receipt_{user.id}.jpg"  # Unique filename for each user
    await photo_file.download_to_drive(temp_filename)

    # Process the receipt using your existing functions
    if extract_and_save_data(temp_filename):
        with open("receipt_data.json", "r") as f:
            extracted_data = json.load(f)

        if write_to_sheet(extracted_data):
            await update.message.reply_text("Data successfully saved to Google Sheet!")
        else:
            await update.message.reply_text("Error writing to Google Sheet.")
    else:
        await update.message.reply_text("Error processing receipt.")

    # Clean up the temporary file (important!)
    os.remove(temp_filename)

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("Send me a photo of your grocery receipt, and I'll extract the data and save it to your Google Sheet.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, process_receipt))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()

if __name__ == "__main__":
    main()