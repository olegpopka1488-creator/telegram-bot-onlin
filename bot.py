import os
import json
import random
import difflib
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_СЮДА")
FACTS_FILE = "facts_ru.json"
MEMORY_FILE = "memory.json"


def safe_load_json(file_path, default):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) or isinstance(data, list):
                    return data
        except json.JSONDecodeError:
            pass
    return default


FACTS = safe_load_json(FACTS_FILE, [])
MEMORY = safe_load_json(MEMORY_FILE, {})


def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(MEMORY, f, ensure_ascii=False, indent=2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет, я умный бот 🤖. Учусь у твоих слов.")


def get_similar_phrase(text, dataset, threshold=0.6):
    if not dataset:
        return None
    best_match = difflib.get_close_matches(text, dataset, n=1, cutoff=threshold)
    return best_match[0] if best_match else None


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip().lower()

    if user_id not in MEMORY:
        MEMORY[user_id] = {"messages": [], "pairs": {}}

    MEMORY[user_id]["messages"].append(text)

    reply = None
    messages = MEMORY[user_id]["messages"]
    pairs = MEMORY[user_id]["pairs"]

    if len(messages) > 1:
        prev = messages[-2]
        if prev not in pairs:
            pairs[prev] = []
        if text not in pairs[prev]:
            pairs[prev].append(text)
        save_memory()

    all_pairs = {k: v for user in MEMORY.values() for k, v in user["pairs"].items()}
    similar = get_similar_phrase(text, all_pairs.keys())

    if similar:
        reply = random.choice(all_pairs[similar])
    elif any(word in text for word in ["факт", "интересно"]):
        reply = random.choice(FACTS) if FACTS else "Фактов пока нет 😏"
    elif any(word in text for word in ["привет", "здравствуй", "хай"]):
        reply = random.choice(["Привет 😎", "Хай!", "Здравствуй!"])
    elif any(word in text for word in ["пока", "до встречи", "увидимся"]):
        reply = random.choice(["Пока 👋", "До скорого!", "Ещё увидимся!"])
    else:
        reply = random.choice([
            f"Интересно, {text}...",
            "Продолжай, я запоминаю 🤔",
            "Расскажи подробнее 😏"
        ])

    await update.message.reply_text(reply)


async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    replies = ["Классный стикер 😎", "Хаха, прикольно 😂", "Люблю стикеры 🤖"]
    await update.message.reply_text(random.choice(replies))


application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
application.add_handler(MessageHandler(filters.STICKER, sticker_reply))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    url = os.environ.get("RENDER_EXTERNAL_URL", "https://telegram-bot-onlin.onrender.com")

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{url}/webhook"
    )

