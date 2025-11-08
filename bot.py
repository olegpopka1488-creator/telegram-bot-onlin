import os
import json
import random
import difflib
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"
MEMORY_FILE = "memory.json"
MAX_MEMORY_SIZE = 50 * 1024 * 1024

def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(file_path, data):
    try:
        data_str = json.dumps(data, ensure_ascii=False, indent=2)
        if len(data_str.encode("utf-8")) > MAX_MEMORY_SIZE:
            for k in list(data.keys())[:len(data)//3]:
                data.pop(k)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

MEMORY = load_json(MEMORY_FILE)
if "dialogs" not in MEMORY:
    MEMORY["dialogs"] = {}
if "keywords" not in MEMORY:
    MEMORY["keywords"] = {}

def normalize(text):
    return re.sub(r"[^а-яА-Яa-zA-Z0-9\s?!.,]", "", text.lower().strip())

def extract_keywords(text):
    words = [w for w in re.findall(r"\w+", text) if len(w) > 3]
    return list(set(words))

def find_best_match(text, memory):
    best, ratio = None, 0
    for k in memory.keys():
        r = difflib.SequenceMatcher(None, text, k).ratio()
        if r > ratio:
            ratio, best = r, k
    return best if ratio > 0.55 else None

def generate_question(base):
    starts = ["А почему", "Что ты думаешь о том, что", "Интересно, а если", "А как ты считаешь,"]
    return f"{random.choice(starts)} {base}?"

def pseudo_think(user_text):
    thoughts = ["Это заставляет задуматься...", "Любопытная идея 🤔", "Хмм... интересно", "Мозг кипит 😄"]
    if "?" in user_text:
        return random.choice(["Хороший вопрос!", "Сложно, но попробую ответить...", "Интересный вопрос 🤖"])
    if any(w in user_text for w in ["люблю", "нравится", "хорошо"]):
        return random.choice(["Рад это слышать!", "Это приятно ❤️", "Класс!"])
    if any(w in user_text for w in ["плохо", "грустно", "ужасно"]):
        return random.choice(["Не унывай", "Все наладится", "Держись 💪"])
    return random.choice(thoughts)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Сознание активировано. Готов к развитию 🤖")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = normalize(update.message.text)
    user_id = str(update.message.from_user.id)
    if user_id not in MEMORY["dialogs"]:
        MEMORY["dialogs"][user_id] = []
    MEMORY["dialogs"][user_id].append(text)
    keywords = extract_keywords(text)
    for w in keywords:
        MEMORY["keywords"].setdefault(w, 0)
        MEMORY["keywords"][w] += 1
    match = find_best_match(text, MEMORY["dialogs"][user_id])
    if match and random.random() < 0.4:
        reply = f"Ты уже говорил про '{match}', интересно, что ты теперь об этом думаешь?"
    else:
        if "?" in text:
            reply = pseudo_think(text)
        elif random.random() < 0.4:
            topic = random.choice(list(MEMORY["keywords"].keys())) if MEMORY["keywords"] else "жизнь"
            reply = generate_question(topic)
        else:
            reply = pseudo_think(text)
    MEMORY["dialogs"][user_id] = MEMORY["dialogs"][user_id][-100:]
    save_json(MEMORY_FILE, MEMORY)
    await update.message.reply_text(reply)

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(["🔥", "😎", "😂", "❤️", "👍", "💪", "🤖", "✨"]))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
app.add_handler(MessageHandler(filters.Sticker.ALL, sticker_reply))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    webhook_url = os.environ.get("WEBHOOK_URL", "https://telegram-bot-onlin.onrender.com")
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{webhook_url}/webhook"
    )

