import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import random

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"

app = Flask(__name__)
bot = Bot(token=TOKEN)
application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен! Привет 😎")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.lower()
    responses = []

    if any(word in text for word in ["привет", "здравствуй", "здорово", "хай"]):
        responses = ["Привет, рад тебя видеть 😎", "Хай! Как настроение?", "Здорово! Давай общаться 😏"]
    elif any(word in text for word in ["как дела", "чё как", "как жизнь", "как сам", "как ты"]):
        responses = ["Всё отлично, у меня всегда хороший день 🤖", "Дела идут нормально, а у тебя?", "Живем и работаем! 😎"]
    elif any(word in text for word in ["пока", "до свидания", "увидимся", "счастливо"]):
        responses = ["Пока! Ещё увидимся 👋", "До скорого!", "Удачи, не скучай!"]
    elif any(word in text for word in ["что нового", "новости", "расскажи", "как там"]):
        responses = ["Всё стабильно, продолжаем работу 💻", "Ничего особенного, а у тебя что нового?", "Работаем и двигаемся вперёд!"]
    elif any(word in text for word in ["бот", "ты кто", "кто ты", "ты"]):
        responses = ["Да, это я! Готов отвечать 😏", "Я твой бот-помощник 🤖", "Просто робот, но с хорошим чувством юмора 😎"]
    else:
        responses = [f"Ты сказал: {update.message.text}", "Я тебя понял!", "Хм… интересно 😏"]

    reply = random.choice(responses)
    await update.message.reply_text(reply)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.create_task(application.process_update(update))
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Бот работает!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

