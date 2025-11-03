import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен! Привет 😎")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower() if update.message and update.message.text else ""

    if any(word in text for word in ["привет", "здравствуй", "хай", "ку"]):
        reply = "Привет, рад тебя видеть 😎"
    elif any(phrase in text for phrase in ["как дела", "что как", "как ты", "как настроение"]):
        reply = "Всё отлично, у меня всегда всё под контролем 🤖"
    elif any(word in text for word in ["пока", "до встречи", "бай", "свидания"]):
        reply = "Пока! Ещё увидимся 👋"
    elif any(word in text for word in ["спасибо", "благодарю"]):
        reply = "Всегда пожалуйста 😉"
    elif any(word in text for word in ["ты кто", "кто ты", "что ты"]):
        reply = "Я твой бот-помощник, всегда на связи 🤖"
    else:
        reply = f"Ты сказал: {update.message.text}" if update.message else "Нет текста"

    await update.message.reply_text(reply)

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    url = "https://telegram-bot-onlin.onrender.com"

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{url}/webhook"
    )

