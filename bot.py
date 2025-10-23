import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"
bot = Bot(TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Хочу большого кекса и кока клы")

def echo(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    if "привет" in text:
        reply = "Привет, рад тебя видеть 😎"
    elif "как дела" in text:
        reply = "Всё отлично, я бот — у меня не бывает плохих дней 🤖"
    elif "пока" in text:
        reply = "Пока! Ещё увидимся 👋"
    else:
        reply = f"Ты сказал: {update.message.text}"
    update.message.reply_text(reply)

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

