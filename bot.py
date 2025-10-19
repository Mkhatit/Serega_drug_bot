import os
import logging
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# ---------------- CONFIG ----------------
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID_FILE = "chat_id.txt"
REMINDER_TIME_HOUR = 15  # 14:00 = до 15:00
REMINDER_MESSAGE = "🔔 Напоминание: выпей таблеточки, Солнце!"
# ----------------------------------------

logging.basicConfig(level=logging.INFO)
scheduler = AsyncIOScheduler()

async def send_reminder(bot: Bot):
    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, "r") as f:
            chat_id = f.read().strip()
        if chat_id:
            await bot.send_message(chat_id=chat_id, text=REMINDER_MESSAGE)
    else:
        logging.warning("Chat ID ещё не задан — напиши боту команду /start")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    with open(CHAT_ID_FILE, "w") as f:
        f.write(chat_id)
    await update.message.reply_text(
        "✅ Привет! Я буду напоминать тебе каждый день в 15:00."
    )

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Планируем ежедневное напоминание
    scheduler.add_job(
        lambda: asyncio.create_task(send_reminder(app.bot)),
        CronTrigger(hour=REMINDER_TIME_HOUR, minute=0)
    )
    scheduler.start()

    print("🤖 Бот запущен и ждёт команду /start.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
