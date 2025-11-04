import os
import random
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"

MEMORY_FILE = "memory.json"
FACTS_FILE = "facts_ru.json"

try:
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)
except:
    memory = {}

try:
    with open(FACTS_FILE, "r", encoding="utf-8") as f:
        facts = json.load(f)
except:
    facts = [
        "Медведи умеют плавать и отлично ориентируются в воде.",
        "Бананы – это ягоды, а клубника – нет.",
        "В России находится самое глубокое озеро в мире – Байкал.",
        "Матрешка – традиционная русская деревянная игрушка.",
        "Самый длинный мост в России – мост через Керченский пролив."
    ]

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

def analyze_text(text):
    text = text.lower()
    emotions = {
        "радость": ["привет", "хай", "здравствуй", "супер", "отлично"],
        "печаль": ["грустно", "плохо", "печально", "не могу", "уныло"],
        "любопытство": ["что", "как", "почему", "знаешь", "расскажи"]
    }
    for emo, words in emotions.items():
        if any(word in text for word in words):
            return emo
    return "нейтрально"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я живой бот 🤖. Давай пообщаемся!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    user_id = str(update.message.from_user.id)

    if user_id not in memory:
        memory[user_id] = {"history": [], "learned": []}
    memory[user_id]["history"].append(user_text)

    # Автообучение: если текст новый, добавляем в список "learned"
    if user_text not in memory[user_id]["learned"]:
        memory[user_id]["learned"].append(user_text)
    save_memory()

    emotion = analyze_text(user_text)

    replies = []
    if emotion == "радость":
        replies = [
            "Рад, что тебе весело 😎",
            "Отлично, позитив заряжает! ✨",
            "Ты в хорошем настроении, я это чувствую!"
        ]
    elif emotion == "печаль":
        replies = [
            "Не грусти, всё будет хорошо 💪",
            "Эх… держись, я с тобой 🤖",
            "Печаль — это нормально, но мы вместе!"
        ]
    elif emotion == "любопытство":
        replies = [
            f"Знаешь что? {random.choice(facts)}",
            "Вот интересный факт: " + random.choice(facts),
            "Любопытно! А вот факт: " + random.choice(facts)
        ]
    else:
        # Автоответы на основе выученного
        learned = memory[user_id]["learned"]
        if learned:
            replies = [f"Ранее ты сказал: {random.choice(learned)}", "Интересно 🤔", "Я тебя понял 🤖"]
        else:
            replies = ["Интересно 🤔", "Я тебя понял 🤖", "Хм… расскажи ещё!"]

    await update.message.reply_text(random.choice(replies))

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker_responses = {
        "happy": ["Весёлый стикер! 😄", "Классный смайл 😎", "Люблю позитивные стикеры! ✨"],
        "sad": ["Ой, грустно 😢", "Надеюсь, скоро станет лучше 😏", "Эх… держись! 💪"],
        "funny": ["Хаха, смешно 😆", "Лол, отличный юмор! 😂", "Я засмеялся 😹"],
        "random": ["Классный стикер! 👍", "Люблю стикеры 😏", "Интересный выбор! 🤖"]
    }
    category = random.choice(list(sticker_responses.keys()))
    await update.message.reply_text(random.choice(sticker_responses[category]))

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

