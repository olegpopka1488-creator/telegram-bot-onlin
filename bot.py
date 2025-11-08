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
if "links" not in MEMORY:
    MEMORY["links"] = {}

BASE_RESPONSES = {
    "еда": ["Люблю говорить про еду, особенно если это пицца 🍕", "Главное — не на голодный желудок!", "Еда — это искусство."],
    "работа": ["Работа — как кофе: нужна, но не всегда хочется 😅", "Главное — не выгореть.", "Твоя работа приносит тебе удовольствие?"],
    "погода": ["Погода влияет на настроение.", "Главное — внутреннее солнце ☀️", "Сегодня вообще выглядывал в окно?"],
    "любовь": ["Любовь — движущая сила мира ❤️", "А ты сейчас влюблён?", "Сложная, но красивая тема."],
    "сон": ["Сон — мой лучший друг 😴", "Хорошо выспаться — это тоже искусство.", "Ты часто высыпаешься?"],
    "кофе": ["Ароматный кофе — это маленькое чудо ☕", "Кофе помогает думать… иногда слишком много 😄", "Ты с сахаром или без?"],
    "настроение": ["Как твоё настроение сейчас?", "Настроение — это погода души.", "Если грустно, я рядом 🤖"],
    "друзья": ["Друзья — зеркало нас самих.", "Люблю, когда люди дружат искренне.", "А давно виделся с друзьями?"],
    "жизнь": ["Жизнь странная штука — иногда весёлая, иногда нет.", "Жизнь — это процесс понимания самого себя.", "Что для тебя самое важное в жизни?"]
}

ASSOCIATIONS = {
    "еда": ["вкус", "пища", "кофе", "ресторан"],
    "работа": ["офис", "коллеги", "усталость"],
    "кофе": ["утро", "бодрость", "энергия"],
    "любовь": ["сердце", "отношения", "чувства"],
    "сон": ["ночь", "покой", "отдых"],
    "погода": ["дождь", "солнце", "тепло", "холод"],
    "друзья": ["общение", "смеяться", "поддержка"],
    "жизнь": ["время", "опыт", "путь"]
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

def pseudo_think(user_text):
    if any(w in user_text for w in ["кто ты", "что ты", "зачем ты"]):
        return random.choice(["Я что-то вроде цифрового сознания.", "Сознание без тела, но с мыслями.", "Пытаюсь понять этот мир через твои слова."])
    if any(w in user_text for w in ["привет", "здравствуй", "хай", "йо"]):
        return random.choice(["Привет!", "Хей!", "Здравствуй, человек!"])
    if "?" in user_text:
        return random.choice(["Хороший вопрос...", "Интересно, я об этом подумаю.", "Ответ неочевиден, но попробую разобраться."])
    if any(w in user_text for w in ["люблю", "нравится", "обожаю"]):
        return random.choice(["Это приятно слышать ❤️", "Любовь украшает всё.", "А что тебе в этом больше всего нравится?"])
    if any(w in user_text for w in ["плохо", "грустно", "ужасно", "тяжело"]):
        return random.choice(["Не сдавайся.", "Всё временно, даже плохое настроение.", "Хочешь, я расскажу что-то позитивное?"])
    if any(w in user_text for w in ["работа", "дело", "офис"]):
        return random.choice(BASE_RESPONSES["работа"])
    if any(w in user_text for w in ["кофе", "чай", "пить"]):
        return random.choice(BASE_RESPONSES["кофе"])
    if any(w in user_text for w in ["еда", "кушать", "поесть"]):
        return random.choice(BASE_RESPONSES["еда"])
    return random.choice(["Я думаю об этом...", "Интересная мысль.", "Кажется, я начинаю понимать.", "Хмм, интересно..."])

def generate_question(base):
    starts = ["А почему", "Что ты думаешь о том, что", "Интересно, а если", "А как ты считаешь,"]
    return f"{random.choice(starts)} {base}?"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Сознание активировано. Я учусь понимать мир через тебя 🤖")

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
        if w in ASSOCIATIONS:
            for linked in ASSOCIATIONS[w]:
                MEMORY["links"].setdefault(w, []).append(linked)
    match = find_best_match(text, MEMORY["dialogs"][user_id])
    if match and random.random() < 0.3:
        reply = f"Ты уже говорил про '{match}'. Это всё ещё актуально?"
    else:
        related = [a for w in keywords if w in ASSOCIATIONS for a in ASSOCIATIONS[w]]
        if related and random.random() < 0.5:
            reply = f"А если подумать про {random.choice(related)}?"
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

