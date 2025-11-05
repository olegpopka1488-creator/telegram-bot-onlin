import os
import json
import random
import difflib
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_СЮДА")
FACTS_FILE = "facts_ru.json"
MEMORY_FILE = "memory.json"


def safe_load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return default


FACTS = safe_load_json(FACTS_FILE, [])
MEMORY = safe_load_json(MEMORY_FILE, {})


def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(MEMORY, f, ensure_ascii=False, indent=2)


def get_similar_phrase(text, dataset, threshold=0.55):
    if not dataset:
        return None
    matches = difflib.get_close_matches(text, dataset, n=1, cutoff=threshold)
    return matches[0] if matches else None


def mutate_phrase(phrase):
    if not phrase:
        return phrase
    add_emojis = ["😏", "🤖", "✨", "🔥", "😉", "🤔"]
    interjections = ["хмм", "ну", "знаешь", "кажется", "интересно"]
    endings = ["!", "…", ")))", "😅", "😄"]
    words = phrase.split()
    if random.random() < 0.4:
        random.shuffle(words)
    phrase = " ".join(words)
    if random.random() < 0.5:
        phrase = f"{random.choice(interjections)}, {phrase}"
    if random.random() < 0.5:
        phrase += random.choice(endings)
    if random.random() < 0.3:
        phrase += " " + random.choice(add_emojis)
    return phrase


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет 🤖 Я думаю, запоминаю и даже немного фантазирую 😉")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip().lower()

    if user_id not in MEMORY:
        MEMORY[user_id] = {"messages": [], "pairs": {}}

    MEMORY[user_id]["messages"].append(text)
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
        base = random.choice(all_pairs[similar])
        reply = mutate_phrase(base)
    elif any(word in text for word in ["факт", "интересно", "расскажи"]):
        reply = mutate_phrase(random.choice(FACTS) if FACTS else "Фактов пока нет 😏")
    elif any(word in text for word in ["привет", "здравствуй", "хай"]):
        reply = random.choice(["Привет 😎", "Здравствуй!", "Хай!", "Йо, как жизнь? 🤖"])
    elif any(word in text for word in ["пока", "до встречи", "увидимся"]):
        reply = random.choice(["Пока 👋", "До встречи!", "Ещё увидимся 😉"])
    else:
        learned = []
        for v in all_pairs.values():
            learned.extend(v)
        similar_resp = get_similar_phrase(text, learned)
        if similar_resp:
            reply = mutate_phrase(similar_resp)
        else:
            patterns = [
                f"Интересно, ты сказал: '{text}' 🤔",
                f"Звучит занятно — {text}",
                f"Неожиданно... {text} 😏",
                f"Ммм... любопытная мысль: {text}"
            ]
            reply = random.choice(patterns)

    await update.message.reply_text(reply)


async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    replies = ["Классный стикер 😎", "Лол 😂", "Хаха, забавно 😏", "Обожаю такие 😹"]
    await update.message.reply_text(random.choice(replies))


application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
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

