from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ContextTypes
import os
import asyncio

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"
bot = Bot(token=TOKEN)
app = Flask(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Хочу большого кекса и кока клы")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(handle_update(update))
    return "ok", 200

async def handle_update(update: Update):
    if update.message and update.message.text:
        text = update.message.text.lower()
        if text.startswith("/start"):
            await start(update, None)
        else:
            await echo(update, None)

@app.route("/")
def index():
    return "Бот работает через Render 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

