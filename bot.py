import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен! Привет 😎")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower() if update.message and update.message.text else ""
    replies = []

    if any(word in text for word in ["привет", "здравствуй", "хай"]):
        replies = ["Привет, рад тебя видеть 😎", "Хай! Как дела?", "Здравствуй! Рад снова тебя видеть!"]
    elif any(word in text for word in ["как дела", "как ты", "что нового"]):
        replies = ["Всё отлично, у меня всегда хороший день 🤖", 
                   "Отлично, спасибо что спросил 😎", 
                   "Всё круто, готов помогать тебе!"]
    elif any(word in text for word in ["пока", "до свидания", "увидимся"]):
        replies = ["Пока! Ещё увидимся 👋", "До встречи! ✌️", "Прощай! Надеюсь, скоро увидимся!"]
    else:
        replies = [f"Ты сказал: {update.message.text}" if update.message else "Нет текста",
                   "Интересно 😏", "Я тебя понял 🤖"]

    reply = random.choice(replies)
    await update.message.reply_text(reply)

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker_responses = ["Хороший стикер 😎", "Классный стикер! 👍", "Люблю стикеры 😏"]
    await update.message.reply_text(random.choice(sticker_responses))

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
application.add_handler(MessageHandler(filters.STICKER, sticker_reply))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    url = "https://telegram-bot-onlin.onrender.com"

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{url}/webhook"
    )

