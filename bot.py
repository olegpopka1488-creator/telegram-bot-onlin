import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"

app = Flask(__name__)
bot = Bot(token=TOKEN)
application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен! Привет 😎")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower() if update.message else ""
    if "привет" in text:
        reply = "Привет, рад тебя видеть 😎"
    elif "как дела" in text:
        reply = "Всё отлично, у меня всегда хороший день 🤖"
    elif "пока" in text:
        reply = "Пока! Ещё увидимся 👋"
    else:
        reply = update.message.text if update.message else "Нет текста"
    await update.message.reply_text(reply)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

@app.route("/webhook", methods=["POST"])
def webhook():
    from telegram.ext import async_to_sync
    update = Update.de_json(request.get_json(force=True), bot)
    async_to_sync(application.process_update)(update)  # <- синхронно запускаем асинхронный обработчик
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Бот работает!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

