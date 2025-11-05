import os
import json
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"
FACTS_FILE = "facts_ru.json"
MEMORY_FILE = "memory.json"

if os.path.exists(FACTS_FILE):
    with open(FACTS_FILE, "r", encoding="utf-8") as f:
        FACTS = json.load(f)
else:
    FACTS = []

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        MEMORY = json.load(f)
else:
    MEMORY = {}

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(MEMORY, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен! Я учусь на каждом сообщении 😎")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip() if update.message and update.message.text else ""
    user_id = str(update.message.from_user.id)

    if user_id not in MEMORY:
        MEMORY[user_id] = []

    MEMORY[user_id].append(text)
    save_memory()

    replies = []
    text_lower = text.lower()

    if any(word in text_lower for word in ["привет", "здравствуй", "хай"]):
        replies = ["Привет, рад тебя видеть 😎", "Хай! Как дела?", "Здравствуй! Рад снова тебя видеть!"]
    elif any(word in text_lower for word in ["как дела", "как ты", "что нового"]):
        replies = ["Всё отлично, у меня всегда хороший день 🤖",
                   "Отлично, спасибо что спросил 😎",
                   "Всё круто, готов помогать тебе!"]
    elif any(word in text_lower for word in ["пока", "до свидания", "увидимся"]):
        replies = ["Пока! Ещё увидимся 👋", "До встречи! ✌️", "Прощай! Надеюсь, скоро увидимся!"]
    elif any(word in text_lower for word in ["факт", "расскажи", "интересно"]):
        if FACTS:
            replies = [random.choice(FACTS)]
        else:
            replies = ["Пока фактов нет 😏"]
    else:
        replies = [f"Ты сказал: {text}", "Интересно 😏", "Я тебя понял 🤖"]

    await update.message.reply_text(random.choice(replies))

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker_responses = ["🔥", "😎", "😂", "❤️", "👍", "💪", "🤖", "✨"]
    await update.message.reply_text(random.choice(sticker_responses))

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
application.add_handler(MessageHandler(filters.STICKER, sticker_reply))

if __name__ == "__main__":
    if os.environ.get("RENDER") is None:
        application.run_polling()
    else:
        port = int(os.environ.get("PORT", 10000))
        webhook_url = os.environ.get("WEBHOOK_URL", "https://telegram-bot-onlin.onrender.com")
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="webhook",
            webhook_url=f"{webhook_url}/webhook"
        )

