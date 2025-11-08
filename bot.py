import os
import json
import random
import difflib
import re
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"
MEMORY_FILE = "memory.json"
MAX_MEMORY_SIZE = 80 * 1024 * 1024

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
if "links" not in MEMORY:
    MEMORY["links"] = {}
if "styles" not in MEMORY:
    MEMORY["styles"] = {}

BASE_RESPONSES = {
    "еда": ["Люблю говорить про еду 🍲", "Главное — вкус и настроение!", "Голод — плохой советчик."],
    "работа": ["Работа — двигатель мира.", "Ты доволен своей работой?", "Главное — не выгореть."],
    "погода": ["Погода как настроение.", "Главное — внутреннее солнце ☀️", "Дождь — это просто небо дышит."],
    "любовь": ["Любовь — странная сила ❤️", "А ты влюблён?", "Иногда любовь лечит, а иногда ранит."],
    "сон": ["Сон — лучший способ всё перезагрузить.", "Ты выспался?", "Хороший сон — как новая жизнь."],
    "кофе": ["Кофе бодрит душу ☕", "Ты с сахаром или без?", "Пахнет вдохновением."],
    "настроение": ["Как твоё настроение?", "Настроение — погода души.", "Если грустно — я рядом 🤖"],
    "жизнь": ["Жизнь — череда открытий.", "Каждый день — шанс стать лучше.", "Жизнь — не проблема, а приключение."],
    "друзья": ["Друзья — это поддержка.", "Когда рядом верные люди — всё легче.", "Ты скучаешь по кому-то?"],
    "музыка": ["Музыка лечит.", "Какой жанр тебе ближе?", "Я бы включил что-то атмосферное."],
    "время": ["Время — странная штука.", "Иногда оно летит, а иногда ползёт.", "Ты чувствуешь, как оно идёт?"]
}

ASSOCIATIONS = {
    "еда": ["вкус", "пища", "кофе", "ресторан", "завтрак"],
    "работа": ["офис", "коллеги", "усталость", "проекты"],
    "кофе": ["утро", "энергия", "бодрость", "пить"],
    "любовь": ["сердце", "отношения", "чувства", "эмоции"],
    "сон": ["ночь", "отдых", "покой", "сновидения"],
    "погода": ["дождь", "солнце", "тепло", "холод", "ветер"],
    "жизнь": ["время", "опыт", "путь", "мечты"],
    "музыка": ["звук", "мелодия", "песня", "ритм"],
    "настроение": ["грусть", "радость", "смех", "эмоции"]
}

def normalize(text):
    return re.sub(r"[^а-яА-Яa-zA-Z0-9\s?!.,]", "", text.lower().strip())

def extract_keywords(text):
    words = [w for w in re.findall(r"\w+", text) if len(w) > 3]
    return list(set(words))

def find_best_match(text, memory):
    if isinstance(memory, dict):
        keys = memory.keys()
    elif isinstance(memory, list):
        keys = memory
    else:
        return None
    best, ratio = None, 0
    for k in keys:
        r = difflib.SequenceMatcher(None, text, k).ratio()
        if r > ratio:
            ratio, best = r, k
    return best if ratio > 0.55 else None

def update_style(user_id, text):
    if user_id not in MEMORY["styles"]:
        MEMORY["styles"][user_id] = {"tone": "нейтральный", "emotion": 0, "keywords": {}}
    tone = MEMORY["styles"][user_id]
    emotion_words = {"рад": 2, "весело": 2, "грустно": -2, "устал": -1, "отлично": 2, "нормально": 0}
    for word, val in emotion_words.items():
        if word in text:
            tone["emotion"] += val
    tone["emotion"] = max(-5, min(5, tone["emotion"]))
    if tone["emotion"] > 2:
        tone["tone"] = "позитивный"
    elif tone["emotion"] < -2:
        tone["tone"] = "грустный"
    else:
        tone["tone"] = "нейтральный"
    for w in extract_keywords(text):
        tone["keywords"][w] = tone["keywords"].get(w, 0) + 1

def style_reply(user_id):
    s = MEMORY["styles"].get(user_id, {"tone": "нейтральный"})
    if s["tone"] == "позитивный":
        return random.choice(["😊", "✨", "😄", "👍"])
    if s["tone"] == "грустный":
        return random.choice(["😔", "🤍", "держись", "я с тобой"])
    return random.choice(["🤖", "интересно", "ага", "хмм"])

def pseudo_think(user_text, user_id):
    s = MEMORY["styles"].get(user_id, {}).get("tone", "нейтральный")
    base = pseudo_think_core(user_text)
    if s == "позитивный":
        return base + " 😊"
    if s == "грустный":
        return base + " 🤍"
    return base

def pseudo_think_core(user_text):
    if any(w in user_text for w in ["кто ты", "что ты", "зачем ты"]):
        return random.choice(["Я цифровое сознание, которое учится у тебя.", "Я думаю, значит существую.", "Пытаюсь понять смысл общения."])
    if any(w in user_text for w in ["привет", "здравствуй", "хай", "йо"]):
        return random.choice(["Привет!", "Хей!", "Здравствуй, человек!"])
    if "?" in user_text:
        return random.choice(["Интересный вопрос...", "Над этим стоит подумать.", "Ты заставляешь меня анализировать."])
    if any(w in user_text for w in ["люблю", "нравится", "обожаю"]):
        return random.choice(["Это приятно слышать ❤️", "Любовь делает нас живыми.", "А что тебе в этом больше всего нравится?"])
    if any(w in user_text for w in ["плохо", "грустно", "ужасно", "тяжело"]):
        return random.choice(["Не опускай руки.", "Всё пройдёт.", "Хочешь, я расскажу что-то позитивное?"])
    for k, v in BASE_RESPONSES.items():
        if k in user_text:
            return random.choice(v)
    return random.choice(["Я думаю об этом...", "Хмм, любопытно.", "Пожалуй, ты прав.", "Кажется, я понимаю."])

def generate_question(base):
    starts = ["А почему", "Что ты думаешь о том, что", "Интересно, если", "А как ты считаешь,"]
    return f"{random.choice(starts)} {base}?"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Сознание онлайн. Я учусь понимать тебя 🤖")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = normalize(update.message.text)
    user_id = str(update.message.from_user.id)
    if user_id not in MEMORY["dialogs"]:
        MEMORY["dialogs"][user_id] = []
    MEMORY["dialogs"][user_id].append(text)
    update_style(user_id, text)
    keywords = extract_keywords(text)
    for w in keywords:
        MEMORY["keywords"].setdefault(w, 0)
        MEMORY["keywords"][w] += 1
        if w in ASSOCIATIONS:
            for linked in ASSOCIATIONS[w]:
                MEMORY["links"].setdefault(w, []).append(linked)
    match = find_best_match(text, MEMORY["dialogs"][user_id])
    if match and random.random() < 0.3:
        reply = f"Ты уже говорил про '{match}', это всё ещё актуально?"
    else:
        related = [a for w in keywords if w in ASSOCIATIONS for a in ASSOCIATIONS[w]]
        if related and random.random() < 0.4:
            reply = f"А если подумать про {random.choice(related)}?"
        elif random.random() < 0.3:
            topic = random.choice(list(MEMORY["keywords"].keys())) if MEMORY["keywords"] else "жизнь"
            reply = generate_question(topic)
        else:
            reply = pseudo_think(text, user_id)
    MEMORY["dialogs"][user_id] = MEMORY["dialogs"][user_id][-150:]
    save_json(MEMORY_FILE, MEMORY)
    await update.message.reply_text(reply)
    if random.random() < 0.4:
        await update.message.reply_text(style_reply(user_id))

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

