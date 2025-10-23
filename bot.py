from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"

app = Flask(__name__)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, update_queue=None, workers=0, use_context=True)

async def start(update, context):
    await update.message.reply_text("Хочу большого кекса и кока клы")

async def echo(update, context):
    text = update.message.text.lower()
    if "привет" in text:
        reply = "Привет, рад тебя видеть 😎"
    elif "как дела" in text:
        reply = "Всё отлично, я бот — у меня не бывает плохих дней 🤖"
    elif "пока" in text:
        reply = "Пока! Ещё увидимся 👋"
    else:
        reply = f"Ты сказал: {update.message.text}"
    await update.message.reply_text(reply)

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp.process_update(update)
    return "OK"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

