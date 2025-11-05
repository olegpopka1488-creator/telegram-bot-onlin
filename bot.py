import os
import json
import random
import difflib
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_СЮДА")
MEMORY_FILE = "memory.json"
FACTS_FILE = "facts_ru.json"

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if not data:
                    return default
                return json.loads(data)
        except Exception as e:
            logging.error(f"Ошибка загрузки {path}: {e}")
            return default
    return default

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"✅ Память сохранена: {path}")
    except Exception as e:
        logging.error(f"❌ Ошибка сохранения {path}: {e}")

MEMORY = load_json(MEMORY_FILE, {})
FACTS = load_json(FACTS_FILE, ["Интересный факт: кофе был открыт пастухом в Эфиопии ☕"])

def find_similar(text, dataset, threshold=0.6):
    if not dataset:
        return None
    matches = difflib.get_close_matches(text, dataset, n=1, cutoff=threshold)
    return matches[0] if matches else None

def mutate_phrase(phrase):
    emojis = ["😎", "🤔", "😉", "✨", "🔥", "😄"]
    interj = ["хмм", "ну", "знаешь", "интересно", "вот так"]
    endings = ["!", "…", ")))", "😅"]
    if random.random() < 0.3:
        phrase = f"{random.choice(interj)}, {phrase}"
    if random.random() < 0.4:
        phrase += random.choice(endings)
    if random.random() < 0.4:
        phrase += " " + random.choice(emojis)
    return phrase

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет 🤖 Я учусь с каждым сообщением 😎")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip().lower()
    user_id = str(update.message.from_user.id)

    if user_id not in MEMORY:
        MEMORY[user_id] = {"context": [], "responses": {}}

    user_mem = MEMORY[user_id]
    context_list = user_mem["context"]
    responses = user_mem["responses"]

    context_list.append(user_text)
    if len(context_list) > 2:
        prev = context_list[-2]
        if prev not in responses:
            responses[prev] = []
        if user_text not in responses[prev]:
            responses[prev].append(user_text)

    all_phrases = {k: v for mem in MEMORY.values() for k, v in mem["responses"].items()}
    similar = find_similar(user_text, all_phrases.keys())

    if similar:
        reply = mutate_phrase(random.choice(all_phrases[similar]))
    elif any(word in user_text for word in ["факт", "интересно", "расскажи"]):
        reply = random.choice(FACTS)
    else:
        reply = random.choice([
            f"Интересная мысль: {user_text} 🤔",
            f"Ты сказал: {user_text} — звучит любопытно!",
            f"Ммм… любопытно: {user_text}",
        ])

    save_json(MEMORY_FILE, MEMORY)
    await update.message.reply_text(reply)
    logging.info(f"💾 Обновлена память для {user_id}")

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(["🔥", "😂", "😎", "✨", "😉"]))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.add_handler(MessageHandler(filters.STICKER, sticker_reply))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    url = os.getenv("RENDER_EXTERNAL_URL", "https://telegram-bot-onlin.onrender.com")
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{url}/webhook"
    )

