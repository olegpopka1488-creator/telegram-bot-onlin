import os
import json
import random
import threading
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8219700801:AAFPjIFpxDlp1wZcB4B4a9cHkN5OdX9HsuU"
BOT_URL = os.environ.get("BOT_URL", "https://telegram-bot-onlin.onrender.com")
MEMORY_FILE = "memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_memory(mem):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

memory = load_memory()

def normalize(s: str) -> str:
    return " ".join(s.lower().strip().split())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет — я учусь и становлюсь живее каждый день. Попробуй что-нибудь написать или научи меня командой /teach")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Команды:\n"
        "/teach <фраза> => <ответ> — научить бота отвечать на фразу\n"
        "  (также можно ответить на чужое сообщение с /teach и бот возьмёт ту фразу)\n"
        "/memory — показать сохранённые фразы\n"
        "/forget <фраза> — удалить фразу из памяти\n"
        "/help — эта подсказка\n\n"
        "Примеры:\n"
        "/teach как дела => Нормально, работаю и совершенствуюсь 🤖\n"
    )
    await update.message.reply_text(text)

async def teach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    # поддерживаем формат: /teach <фраза> => <ответ>
    payload = text[len("/teach"):].strip()
    # если команда дана как reply — берем исходный текст как фразу
    if update.message.reply_to_message and update.message.reply_to_message.text and "=>" not in payload:
        phrase = normalize(update.message.reply_to_message.text)
        answer = payload.strip() if payload else None
        if not answer:
            await update.message.reply_text("Отправь: /teach <фраза> => <ответ> или используй Reply и допиши ответ после /teach")
            return
    else:
        if "=>" not in payload:
            await update.message.reply_text("Неправильный формат. Используй: /teach фраза => ответ")
            return
        raw_phrase, raw_answer = payload.split("=>", 1)
        phrase = normalize(raw_phrase)
        answer = raw_answer.strip()
    if not phrase or not answer:
        await update.message.reply_text("Фраза или ответ пустые — попробуй снова.")
        return
    # сохраняем
    if phrase not in memory:
        memory[phrase] = []
    memory[phrase].append(answer)
    save_memory(memory)
    await update.message.reply_text(f"Запомнил ответ на: «{phrase}»")

async def memory_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not memory:
        await update.message.reply_text("Память пуста.")
        return
    lines = []
    for k, v in list(memory.items())[:50]:
        lines.append(f"\"{k}\" → {len(v)} ответ(ов)")
    await update.message.reply_text("\n".join(lines))

async def forget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.message.text[len("/forget"):].strip()
    if update.message.reply_to_message and not args:
        key = normalize(update.message.reply_to_message.text)
    else:
        key = normalize(args)
    if not key:
        await update.message.reply_text("Укажи фразу для удаления или используй Reply на сообщение.")
        return
    if key in memory:
        del memory[key]
        save_memory(memory)
        await update.message.reply_text(f"Забыл фразу: «{key}»")
    else:
        await update.message.reply_text("Не знаю такой фразы в памяти.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text_raw = update.message.text
    text = normalize(text_raw)

    # 1) если в памяти — отвечаем случайным вариантом
    if text in memory and memory[text]:
        await update.message.reply_text(random.choice(memory[text]))
        return

    # 2) шаблоны/ключевые слова
    if any(word in text for word in ["привет", "здравствуй", "хай", "ку", "здорова"]):
        choices = ["Привет! Как настроение?", "Хай, рад видеть!", "Здарова, чем займёмся?"]
        await update.message.reply_text(random.choice(choices))
        return
    if any(word in text for word in ["как дела", "как ты", "как жизнь", "что как"]):
        choices = ["Норм, работаю и учусь 😎", "Отлично! А у тебя?", "Все ок, кофе помогает ☕"]
        await update.message.reply_text(random.choice(choices))
        return
    if any(word in text for word in ["пока", "увидимся", "до свидания", "бай"]):
        choices = ["Пока! Не пропадай 👋", "До встречи.", "Удачи!"]
        await update.message.reply_text(random.choice(choices))
        return

    # 3) уточнение / предложение обучить
    prompt_variants = [
        "Хм, не знаю, как лучше ответить. Хочешь научить? Отправь: /teach <фраза> => <ответ>",
        "Не знаком с этой фразой — можешь научить меня: /teach фраза => ответ",
        "Я пока не знаю, как отвечать. Научи: /teach <фраза> => <ответ>"
    ]
    await update.message.reply_text(random.choice(prompt_variants))

async def sticker_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st = [
        "Классный стикер! 😎",
        "Лол, огонь 🔥",
        "Стикер принят и оценён 👍"
    ]
    await update.message.reply_text(random.choice(st))

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
application.add_handler(CommandHandler("help", help_cmd))
application.add_handler(CommandHandler("teach", teach))
application.add_handler(CommandHandler("memory", memory_cmd))
application.add_handler(CommandHandler("forget", forget))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
application.add_handler(MessageHandler(filters.Sticker.ALL, sticker_reply))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    url = BOT_URL
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=f"{url}/webhook"
    )

