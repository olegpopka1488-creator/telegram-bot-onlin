import json
import os
import random
import asyncio
import aiohttp
from duckduckgo_search import DDGS
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

MEMORY_FILE = "memory.json"
KNOWLEDGE_FILE = "knowledge_base.json"

def load_json(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

MEMORY = load_json(MEMORY_FILE)
KNOWLEDGE = load_json(KNOWLEDGE_FILE)

async def search_internet(query):
    results = []
    try:
        async with DDGS() as ddgs:
            async for r in ddgs.text(query, max_results=2):
                results.append(r["body"])
    except Exception:
        pass
    if results:
        return " ".join(results[:2])
    return None

def find_best_match(user_id, message):
    user_memory = MEMORY.get(user_id, [])
    for record in user_memory[::-1]:
        if any(word in record["user"].lower() for word in message.lower().split()):
            return record["bot"]
    for k, v in KNOWLEDGE.items():
        if k.lower() in message.lower():
            return v
    return None

async def generate_reply(user_id, message):
    answer = find_best_match(user_id, message)
    if answer:
        return answer

    web_info = await search_internet(message)
    if web_info:
        KNOWLEDGE[message] = web_info
        save_json(KNOWLEDGE_FILE, KNOWLEDGE)
        return web_info

    generic = [
        "Интересная мысль. Расскажи подробнее?",
        "Хм, любопытно! Почему ты так думаешь?",
        "Понимаю тебя. А что ты чувствуешь насчёт этого?",
        "А если посмотреть на это под другим углом?"
    ]
    return random.choice(generic)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip()

    reply = await generate_reply(user_id, text)

    MEMORY.setdefault(user_id, []).append({"user": text, "bot": reply})
    if len(MEMORY[user_id]) > 50:
        MEMORY[user_id] = MEMORY[user_id][-50:]
    save_json(MEMORY_FILE, MEMORY)

    await update.message.reply_text(reply)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я живой бот. Пиши что угодно — поговорим 😊")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run_polling()

