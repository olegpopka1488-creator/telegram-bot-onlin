import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен! Привет 😎")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower() if update.message and update.message.text else ""
    if "привет" in text:
        reply = "Привет, рад тебя видеть 😎"
    elif "как дела" in text:
        reply = "Всё отлично, у меня всегда хороший день 🤖"
    elif "пока" in text:
        reply = "Пока! Ещё увидимся 👋"
    else:
        reply = f"Ты сказал: {update.message.text}" if update.message else "Нет текста"
    await update.message.reply_text(reply)

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    # Настройка webhook Render
    port = int(os.environ.get("PORT", 10000))
    url = f"https://telegram-bot-onlin.onrender.com"
    await application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{url}/webhook"
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

