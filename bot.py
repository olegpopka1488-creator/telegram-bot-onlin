import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import random

logging.basicConfig(level=logging.INFO)

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я живой и готов общаться 😎")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    replies = {
        "привет": [
            "Здарова! Как дела?",
            "Привет! Рад тебя видеть!",
            "О, приветик 😏"
        ],
        "как дела": [
            "Отлично! У тебя как?",
            "Та норм, живу 😄",
            "Потихоньку, главное — не грустить!"
        ],
        "что делаешь": [
            "Считаю байты и думаю о смысле жизни 🤖",
            "Жду, когда ты снова что-нибудь напишешь 😉",
            "Работаю, как всегда!"
        ],
        "ты кто": [
            "Я твой бот, братан 😎",
            "AI с характером, приятно познакомиться!",
            "Тот, кто всегда на связи 💬"
        ],
        "спасибо": [
            "Всегда пожалуйста 🙌",
            "Не за что, я тут для этого 😁",
            "Без проблем!"
        ]
    }

    for key, variants in replies.items():
        if text == key or text == key.capitalize():
            await update.message.reply_text(random.choice(variants))
            return

    await update.message.reply_text("Не понял 😅 Но я учусь каждый день!")

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен и ждёт сообщений 🚀")
    application.run_polling()

if __name__ == "__main__":
    main()

