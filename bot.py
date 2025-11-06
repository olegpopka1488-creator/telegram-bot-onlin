import os
import json
import random
import difflib
import threading
import http.server
import socketserver
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"
MEMORY_FILE = "memory.json"
MAX_MEMORY_SIZE = 50 * 1024 * 1024

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except:
            return {}
    return {}

def save_memory(mem):
    data_str = json.dumps(mem, ensure_ascii=False, indent=2)
    if len(data_str.encode('utf-8')) > MAX_MEMORY_SIZE:
        keys = list(mem.keys())
        for _ in range(len(keys)//2):
            mem.pop(random.choice(keys), None)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

memory = load_memory()

def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())

def find_similar(text, memory):
    best_match, best_ratio = None, 0
    for phrase in memory.keys():
        ratio = difflib.SequenceMatcher(None, text, phrase).ratio()
        if ratio > best_ratio:
            best_ratio, best_match = ratio, phrase
    return best_match if best_ratio > 0.6 else None

def mutate_phrase(phrase):
    add_emojis = ["😎", "🤖", "😉", "🔥", "💭", "😏", "🤔", "✨"]
    interjections = ["ммм", "хмм", "слушай", "интересно", "кажется", "ну"]
    endings = ["!", "…", ")))", "😅", "😄", "😜"]
    words = phrase.split()
    random.shuffle(words)
    mutated = " ".join(words)
    if random.random() < 0.4:
        mutated = f"{random.choice(interjections)}, {mutated}"
    if random.random() < 0.5:
        mutated += random.choice(endings)
    if random.random() < 0.3:
        mutated += " " + random.choice(add_emojis)
    return mutated.strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я теперь учусь на каждом сообщении 😎")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = normalize(update.message.text)
    response = None
    match = find_similar(user_text, memory)
    if match:
        base_response = random.choice(memory[match])
        response = mutate_phrase(base_response)
    else:
        base_responses = [
            "Интересно… расскажи подробнее 🤔",
            "Хмм, не думал об этом 😏",
            "Любопытно 😄",
            "Ты меня заинтриговал 😎",
            "Это звучит необычно 🤖"
        ]
        response = random.choice(base_responses)
    await update.message.reply_text(response)
    if user_text not in memory:
        memory[user_text] = []
    if response not in memory[user_text]:
        memory[user_text].append(response)
    save_memory(memory)

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st = ["🔥", "😎", "😂", "❤️", "👍", "💪", "🤖", "✨"]
    await update.message.reply_text(random.choice(st))

def keep_port_open():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=keep_port_open, daemon=True).start()

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
application.add_handler(MessageHandler(filters.ALL & filters.Sticker.ALL, sticker_reply))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    webhook_url = os.environ.get("WEBHOOK_URL", "https://telegram-bot-onlin.onrender.com")
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{webhook_url}/webhook"
    )

