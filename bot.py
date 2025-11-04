import os
import json
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"
FACTS_FILE = "facts_ru.json"
MEMORY_FILE = "memory.json"

def load_json(file_path, default):
if os.path.exists(file_path):
try:
with open(file_path, "r", encoding="utf-8") as f:
content = f.read().strip()
return json.loads(content) if content else default
except:
return default
return default

FACTS = load_json(FACTS_FILE, [])
MEMORY = load_json(MEMORY_FILE, {})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await update.message.reply_text("Бот запущен! Привет 😎")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
text = update.message.text.strip() if update.message and update.message.text else ""
user_id = str(update.message.from_user.id)

```
if user_id not in MEMORY:
    MEMORY[user_id] = []

MEMORY[user_id].append(text)

with open(MEMORY_FILE, "w", encoding="utf-8") as f:
    json.dump(MEMORY, f, ensure_ascii=False, indent=2)

replies = []
text_lower = text.lower()

if any(word in text_lower for word in ["привет", "здравствуй", "хай"]):
    replies = ["Привет, рад тебя видеть 😎", "Хай! Как дела?", "Здравствуй! Рад снова тебя видеть!"]
elif any(word in text_lower for word in ["как дела", "как ты", "что нового"]):
    replies = ["Всё отлично, у меня всегда хороший день 🤖", 
               "Отлично, спасибо что спросил 😎", 
               "Всё круто, готов помогать тебе!"]
elif any(word in text_lower for word in ["пока", "до свидания", "увидимся"]):
    replies = ["Пока! Ещё увидимся 👋", "До встречи! ✌️", "Прощай! Надеюсь, скоро увидимся!"]
elif any(word in text_lower for word in ["факт", "расскажи", "интересно"]):
    replies = [random.choice(FACTS)] if FACTS else ["Пока фактов нет 😏"]
else:
    replies = [f"Ты сказал: {text}", "Интересно 😏", "Я тебя понял 🤖"]

await update.message.reply_text(random.choice(replies))
```

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
sticker_responses = {
"happy": ["Весёлый стикер! 😄", "Классный смайл 😎", "Люблю позитивные стикеры! ✨"],
"sad": ["Ой, грустно 😢", "Надеюсь, скоро станет лучше 😏", "Эх… держись! 💪"],
"funny": ["Хаха, смешно 😆", "Лол, отличный юмор! 😂", "Я засмеялся 😹"],
"random": ["Классный стикер! 👍", "Люблю стикеры 😏", "Интересный выбор! 🤖"]
}
category = random.choice(list(sticker_responses.keys()))
await update.message.reply_text(random.choice(sticker_responses[category]))

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
application.add_handler(MessageHandler(filters.Sticker.ALL, sticker_reply))

if **name** == "**main**":
port = int(os.environ.get("PORT", 10000))
url = "[https://telegram-bot-onlin.onrender.com](https://telegram-bot-onlin.onrender.com)"

```
application.run_webhook(
    listen="0.0.0.0",
    port=port,
    url_path="webhook",
    webhook_url=f"{url}/webhook"
)
```

