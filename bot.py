import os
import json
import random
import difflib
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"
MEMORY_FILE = "memory.json"
FACTS_FILE = "facts_ru.json"
MAX_MEMORY_SIZE = 50 * 1024 * 1024

def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) or isinstance(data, list):
                    return data
        except:
            return {} if file_path.endswith(".json") else []
    return {} if file_path.endswith(".json") else []

def save_json(file_path, data):
    data_str = json.dumps(data, ensure_ascii=False, indent=2)
    if len(data_str.encode("utf-8")) > MAX_MEMORY_SIZE:
        if isinstance(data, dict):
            keys = list(data.keys())
            for _ in range(len(keys)//2):
                data.pop(random.choice(keys), None)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

MEMORY = load_json(MEMORY_FILE)
FACTS = load_json(FACTS_FILE)

def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())

def find_similar(text, memory):
    best_match, best_ratio = None, 0
    for phrase in memory.keys():
        ratio = difflib.SequenceMatcher(None, text, phrase).ratio()
        if ratio > best_ratio:
            best_ratio, best_match = ratio, phrase
    return best_match if best_ratio > 0.6 else None

def mutate_response(response):
    emojis = ["😎","🤖","😉","🔥","💭","😏","🤔","✨"]
    interjections = ["ммм","хмм","слушай","интересно","кажется","ну"]
    endings = ["!", "…", ")))","😅","😄","😜"]
    words = response.split()
    random.shuffle(words)
    mutated = " ".join(words)
    if random.random() < 0.4:
        mutated = f"{random.choice(interjections)}, {mutated}"
    if random.random() < 0.5:
        mutated += random.choice(endings)
    if random.random() < 0.3:
        mutated += " " + random.choice(emojis)
    return mutated.strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я учусь на каждом сообщении 😎")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = normalize(update.message.text)
    user_id = str(update.message.from_user.id)
    if user_id not in MEMORY:
        MEMORY[user_id] = []
    MEMORY[user_id].append(text)
    save_json(MEMORY_FILE, MEMORY)

    match = find_similar(text, MEMORY)
    if match:
        response = mutate_response(random.choice(MEMORY[match]))
    else:
        base_responses = [
            "Интересно… расскажи подробнее 🤔",
            "Хмм, не думал об этом 😏",
            "Любопытно 😄",
            "Ты меня заинтриговал 😎",
            "Это звучит необычно 🤖"
        ]
        response = random.choice(base_responses)
        if text not in MEMORY:
            MEMORY[text] = []
        MEMORY[text].append(response)
        save_json(MEMORY_FILE, MEMORY)

    if any(word in text for word in ["факт","расскажи","интересно"]) and FACTS:
        response = random.choice(FACTS)

    await update.message.reply_text(response)

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    responses = ["🔥","😎","😂","❤️","👍","💪","🤖","✨"]
    await update.message.reply_text(random.choice(responses))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    webhook_url = os.environ.get("WEBHOOK_URL", "https://telegram-bot-onlin.onrender.com")
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{webhook_url}/webhook"
    )

