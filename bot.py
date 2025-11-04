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
MEMORY_FILE = "smart_memory.json"
FACTS_FILE = "facts.json"

def load_json(file):
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

memory = load_json(MEMORY_FILE)

def load_facts():
    try:
        res = requests.get("https://catfact.ninja/facts?limit=50", timeout=10)
        if res.status_code == 200:
            facts = [f["fact"] for f in res.json().get("data", [])]
            save_json(FACTS_FILE, facts)
            return facts
    except:
        pass
    local = load_json(FACTS_FILE)
    if isinstance(local, list):
        return local
    return []

facts_base = load_facts()

def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())

def find_similar(text, memory):
    best_match, best_ratio = None, 0
    for phrase in memory.keys():
        ratio = difflib.SequenceMatcher(None, text, phrase).ratio()
        if ratio > best_ratio:
            best_ratio, best_match = ratio, phrase
    return best_match if best_ratio > 0.6 else None

def detect_mood(text):
    text = text.lower()
    moods = {
        "happy": ["ура", "супер", "класс", "весело", "хорошо", "смеюсь", "ха", "😁", "😂", "😄"],
        "sad": ["печаль", "грусть", "плохо", "😭", "😢", "тяжело", "один", "скучно"],
        "angry": ["злюсь", "бесит", "ненавижу", "ужас", "чёрт", "😡", "🤬"],
        "neutral": []
    }
    for mood, words in moods.items():
        if any(w in text for w in words):
            return mood
    return "neutral"

def mutate_phrase(phrase, mood):
    emojis = {
        "happy": ["😄", "😎", "✨", "😂", "🤗"],
        "sad": ["😢", "💔", "🥺", "😞"],
        "angry": ["😤", "😠", "🔥", "💢"],
        "neutral": ["🤖", "😏", "💭"]
    }
    interjections = {
        "happy": ["ха!", "круто!", "супер!", "ух ты!"],
        "sad": ["эх…", "жалко", "печально", "ммм…"],
        "angry": ["чёрт!", "серьёзно?!", "ну блин!", "вот это да!"],
        "neutral": ["хмм", "ну", "понятно", "интересно"]
    }

    phrase = phrase.capitalize()
    phrase += " " + random.choice(emojis[mood])
    if random.random() < 0.5:
        phrase = f"{random.choice(interjections[mood])} {phrase}"
    return phrase.strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я теперь чувствую настроение и учусь на каждом сообщении 🤖")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = normalize(update.message.text)
    mood = detect_mood(user_text)
    response = None

    match = find_similar(user_text, memory)
    if match:
        base_response = random.choice(memory[match])
        response = mutate_phrase(base_response, mood)
    else:
        base_responses = {
            "happy": ["Ты сегодня явно на позитиве!", "Обожаю, когда у кого-то отличное настроение!", "Звучишь очень радостно!"],
            "sad": ["Эй, не грусти!", "Всё наладится, правда 💪", "Если хочешь — расскажи, что случилось."],
            "angry": ["Эээй, не кипятись 😅", "Давай вдохнём и выдохнем 😤", "Понимаю, иногда всё раздражает..."],
            "neutral": ["Интересно 😏", "Хмм, расскажи подробнее 🤔", "Любопытно 🤖"]
        }
        response = random.choice(base_responses[mood])

    if random.random() < 0.25 and facts_base:
        response += f"\nА вот факт: {random.choice(facts_base)}"

    await update.message.reply_text(response)

    if user_text not in memory:
        memory[user_text] = []
    if response not in memory[user_text]:
        memory[user_text].append(response)
    save_json(MEMORY_FILE, memory)

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sticker_replies = ["🔥", "😎", "😂", "❤️", "👍", "💪", "🤖", "✨"]
    await update.message.reply_text(random.choice(sticker_replies))

def keep_alive():
    url = BOT_URL
    while True:
        try:
            requests.get(url, timeout=5)
        except:
            pass
        time.sleep(300)

threading.Thread(target=keep_alive, daemon=True).start()

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
application.add_handler(MessageHandler(filters.Sticker.ALL, sticker_reply))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{BOT_URL}/webhook"
    )

