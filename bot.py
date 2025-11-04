import os
import json
import random
import difflib
import requests
import threading
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"
BOT_URL = os.environ.get("BOT_URL", "https://telegram-bot-onlin.onrender.com")
MEMORY_FILE = "memory.json"
FACTS_FILE = "facts_ru.json"

def load_json(fname):
    try:
        with open(fname, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(fname, data):
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

memory = load_json(MEMORY_FILE)

def fetch_russian_facts():
    # можно заменить на API с русскими фактами
    # пример: брать факты с какого-то открытого источника
    try:
        res = requests.get("https://russian-facts-api.herokuapp.com/facts?limit=50", timeout=10)
        if res.status_code == 200:
            data = res.json()
            facts = data.get("facts", [])
            if isinstance(facts, list):
                save_json(FACTS_FILE, facts)
                return facts
    except:
        pass
    # fallback к локальным фактам
    return load_json(FACTS_FILE)

facts_ru = fetch_russian_facts()

def normalize(s: str) -> str:
    return " ".join(s.lower().strip().split())

def find_similar(text, mem):
    best, br = None, 0
    for p in mem.keys():
        r = difflib.SequenceMatcher(None, text, p).ratio()
        if r > br:
            br, best = r, p
    return best if br > 0.6 else None

def detect_mood(text):
    t = text.lower()
    if any(w in t for w in ["счаст", "рад", "😀", "😄", "хорошо", "весел"]):
        return "happy"
    if any(w in t for w in ["груст", "плохо", "тоска", "😢", "печаль"]):
        return "sad"
    if any(w in t for w in ["злюсь", "злость", "😠", "злой", "бесит"]):
        return "angry"
    return "neutral"

def mutate(resp, mood):
    emojis = {
        "happy": ["😄","✨","😁"],
        "sad": ["😢","💔","😔"],
        "angry": ["😡","🔥","😤"],
        "neutral": ["🤖","😏","..."]
    }
    interj = {
        "happy": ["ура", "вот это да", "классно"],
        "sad": ["эх", "жалко", "увы"],
        "angry": ["чёрт", "ну и дела", "эх"],
        "neutral": ["ммм", "хмм", "интересно"]
    }
    out = resp
    if random.random() < 0.5:
        out = f"{random.choice(interj[mood])}, {out}"
    out += " " + random.choice(emojis[mood])
    return out.strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if uid not in memory:
        memory[uid] = {"name": update.effective_user.first_name, "history": [], "mood": "neutral", "last_active": time.time()}
        save_json(MEMORY_FILE, memory)
    await update.message.reply_text("Привет! Я слушаю и запоминаю.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    text = update.message.text.strip()
    if uid not in memory:
        memory[uid] = {"name": update.effective_user.first_name, "history": [], "mood": "neutral", "last_active": 0}
    memory[uid]["last_active"] = time.time()
    norm = normalize(text)
    memory[uid]["history"].append(norm)
    if len(memory[uid]["history"]) > 20:
        memory[uid]["history"].pop(0)

    mood = detect_mood(text)
    memory[uid]["mood"] = mood

    sim = find_similar(norm, memory)
    if sim and memory.get(sim):
        resp = random.choice(memory[sim].get("responses", [sim]))
        resp = mutate(resp, mood)
    else:
        base = {
            "happy": ["Ты явно в хорошем настроении — здорово!", "Классно услышать такое!", "У тебя позитив сегодня!"],
            "sad": ["Не грусти, расскажи что-то хорошее?", "Сложно? Мне жаль.", "Я рядом, если хочешь поделиться."],
            "angry": ["Что-то тебя зацепило?", "Хм, это злит? Расскажи.", "Я понимаю, бывает…"],
            "neutral": ["Интересно.", "Хмм...", "Расскажи подробнее"]
        }
        resp = random.choice(base[mood])
    if facts_ru and random.random() < 0.2:
        resp += "\nФакт: " + random.choice(facts_ru)

    if "responses" not in memory[uid]:
        memory[uid]["responses"] = {}
    if norm not in memory[uid]["responses"]:
        memory[uid]["responses"][norm] = []
    memory[uid]["responses"][norm].append(resp)

    save_json(MEMORY_FILE, memory)
    await update.message.reply_text(resp)

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(["😄","👍","🤖","🔥","😂"]))

def auto_initiator(application):
    while True:
        now = time.time()
        for uid, udata in memory.items():
            if now - udata.get("last_active", 0) > 3600:  # час без общения
                try:
                    # отправляем сообщение пользователю
                    application.bot.send_message(int(uid), "Привет! Мы давно не говорили 😊")
                except:
                    pass
        time.sleep(600)

def keep_alive():
    while True:
        try:
            requests.get(BOT_URL, timeout=5)
        except:
            pass
        time.sleep(300)

threading.Thread(target=keep_alive, daemon=True).start()

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
application.add_handler(MessageHandler(filters.Sticker.ALL, sticker_reply))

if __name__ == "__main__":
    threading.Thread(target=auto_initiator, args=(application,), daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{BOT_URL}/webhook"
    )

