import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from google import genai

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    chat_type = update.message.chat.type
    bot_username = (await context.bot.get_me()).username
    
    is_mentioned = f"@{bot_username}" in user_text
    is_reply = (update.message.reply_to_message and 
                update.message.reply_to_message.from_user.username == bot_username)

    if chat_type in ["group", "supergroup"] and not (is_mentioned or is_reply):
        return

    clean_prompt = user_text.replace(f"@{bot_username}", "").strip()
    if not clean_prompt:
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=clean_prompt
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Maaf, terjadi kesalahan pada koneksi Gemini AI.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()