import os
import json
import random
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

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
            return {"history": [], "facts": [], "mood": "neutral"}
    return {"history": [], "facts": [], "mood": "neutral"}

def save_memory(mem):
    data_str = json.dumps(mem, ensure_ascii=False, indent=2)
    if len(data_str.encode("utf-8")) > MAX_MEMORY_SIZE:
        mem["history"] = mem["history"][-10000:]
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

memory = load_memory()

def mood_detect(text):
    if re.search(r"\b(плохо|грустно|печально|ужасно|тяжело)\b", text.lower()):
        return "sad"
    if re.search(r"\b(хорошо|супер|отлично|замечательно|рад)\b", text.lower()):
        return "happy"
    if re.search(r"\b(злюсь|бесит|раздражает|ненавижу)\b", text.lower()):
        return "angry"
    return "neutral"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я коллективный разум 🤖 Запоминаю всё, чему меня учат пользователи 😎")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()

    memory["history"].append(user_text)
    if len(memory["history"]) > 20000:
        memory["history"] = memory["history"][-10000:]

    mood = mood_detect(user_text)
    memory["mood"] = mood

    reply_options = {
        "happy": ["Классное настроение 😄", "Так держать!", "Позитив заряжает 🔥"],
        "sad": ["Не грусти 💫", "Это пройдёт ❤️", "Держись, всё будет хорошо 😉"],
        "angry": ["Ого, чувствуется злость 😬", "Попробуй выдохнуть 💭", "Давай остынем немного 🤖"],
        "neutral": ["Интересно 🤔", "Понял тебя 😎", "Хмм, расскажи поподробнее 😉"]
    }

    base_response = random.choice(reply_options[mood])

    if random.random() < 0.4 and len(memory["history"]) > 5:
        prev = random.choice(memory["history"][-5:])
        base_response += f" Кстати, кто-то недавно говорил: “{prev}”."

    await update.message.reply_text(base_response)
    save_memory(memory)

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(["🔥", "😂", "❤️", "👍", "😎", "🤖", "✨", "😉"]))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
app.add_handler(MessageHandler(filters.ALL, sticker_reply))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    webhook_url = os.environ.get("WEBHOOK_URL", "https://telegram-bot-onlin.onrender.com")
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{webhook_url}/webhook"
    )

