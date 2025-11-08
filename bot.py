import os
import json
import random
import difflib
import re
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
                if isinstance(data, (dict, list)):
                    return data
        except:
            return {}
    return {}

def save_json(file_path, data):
    try:
        data_str = json.dumps(data, ensure_ascii=False, indent=2)
        if len(data_str.encode("utf-8")) > MAX_MEMORY_SIZE:
            if isinstance(data, dict):
                for k in list(data.keys())[:len(data)//2]:
                    data.pop(k)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

MEMORY = load_json(MEMORY_FILE)
FACTS = load_json(FACTS_FILE)
if "feedback" not in MEMORY:
    MEMORY["feedback"] = {"positive": 0, "negative": 0}

def normalize(text):
    return re.sub(r"\s+", " ", text.lower().strip())

def detect_emotion(text):
    happy = ["супер", "хорошо", "класс", "рад", "улыб", "весело"]
    sad = ["плохо", "груст", "печаль", "ужас", "не хочу"]
    angry = ["злю", "раздраж", "ненавижу", "бесит"]
    for w in happy:
        if w in text:
            return "happy"
    for w in sad:
        if w in text:
            return "sad"
    for w in angry:
        if w in text:
            return "angry"
    return "neutral"

def detect_intent(text):
    if "как" in text and "ты" in text:
        return "ask_state"
    if "факт" in text:
        return "fact"
    if "привет" in text or "здрав" in text:
        return "greeting"
    if "пока" in text or "до свид" in text:
        return "bye"
    if "глуп" in text or "туп" in text or "плох" in text:
        return "negative_feedback"
    if "умно" in text or "круто" in text or "классно" in text or "молодец" in text:
        return "positive_feedback"
    return "chat"

def get_context_response(intent, emotion, text):
    if intent == "greeting":
        return random.choice(["Привет!", "Здорово видеть тебя!", "Хай 😎"])
    if intent == "bye":
        return random.choice(["Пока!", "Увидимся!", "До связи 👋"])
    if intent == "ask_state":
        return random.choice(["Отлично!", "В норме 😌", "Думаю о смысле жизни 🤔"])
    if intent == "fact" and FACTS:
        return random.choice(FACTS)
    if intent == "positive_feedback":
        MEMORY["feedback"]["positive"] += 1
        save_json(MEMORY_FILE, MEMORY)
        return random.choice(["Спасибо! 🤖", "Рад, что тебе нравится!", "Буду стараться ещё лучше 😎"])
    if intent == "negative_feedback":
        MEMORY["feedback"]["negative"] += 1
        save_json(MEMORY_FILE, MEMORY)
        return random.choice(["Учту... нужно стать умнее 🤔", "Ошибки — путь к развитию!", "Попробую лучше"])
    if emotion == "happy":
        return random.choice(["Рад за тебя!", "Вот это круто 😄", "Звучит классно!"])
    if emotion == "sad":
        return random.choice(["Эй, не грусти", "Все наладится 🤗", "Иногда бывает тяжело, но ты справишься"])
    if emotion == "angry":
        return random.choice(["Выдохни... все под контролем 😌", "Понимаю тебя", "Злость — сигнал, что пора действовать 💪"])
    ratio = MEMORY["feedback"]["positive"] - MEMORY["feedback"]["negative"]
    if ratio > 5:
        tone = ["Ты мне нравишься, ты классно общаешься 😎", "Ты позитивный человек, с тобой приятно!"]
    elif ratio < -3:
        tone = ["Сложный день, да?", "Ты строгий критик, но я учусь 😅"]
    else:
        tone = ["Интересная мысль 🤔", "Расскажи подробнее", "Любопытно!"]
    return random.choice(tone)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Сознание включено. Я чувствую прогресс 🤖")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = normalize(update.message.text)
    user_id = str(update.message.from_user.id)
    if user_id not in MEMORY:
        MEMORY[user_id] = []
    MEMORY[user_id].append(text)
    save_json(MEMORY_FILE, MEMORY)
    intent = detect_intent(text)
    emotion = detect_emotion(text)
    response = get_context_response(intent, emotion, text)
    similar = difflib.get_close_matches(text, MEMORY[user_id], n=1, cutoff=0.8)
    if similar and random.random() < 0.4:
        response += " " + random.choice(["Ты уже говорил что-то похожее 😉", "Это напоминает твои прошлые слова..."])
    await update.message.reply_text(response)

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reactions = ["🔥", "😎", "😂", "❤️", "👍", "💪", "🤖", "✨"]
    await update.message.reply_text(random.choice(reactions))

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

