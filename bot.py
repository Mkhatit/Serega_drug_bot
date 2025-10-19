import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# ---------------- CONFIG ----------------
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID_FILE = "chat_id.txt"
REMINDER_TIME_HOUR = 15
REMINDER_MESSAGE = "🔔 Напоминание: выпей таблеточки, Солнце!"
# ----------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_reminder(application):
    """Отправляет напоминание в сохранённый чат."""
    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, "r") as f:
            chat_id = f.read().strip()
        if chat_id:
            await application.bot.send_message(chat_id=chat_id, text=REMINDER_MESSAGE)
            logger.info(f"✅ Напоминание отправлено ({chat_id})")
    else:
        logger.warning("⚠️ Chat ID ещё не задан — напиши боту команду /start")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохраняет chat_id пользователя при /start."""
    chat_id = str(update.effective_chat.id)
    with open(CHAT_ID_FILE, "w") as f:
        f.write(chat_id)
    await update.message.reply_text("✅ Привет! Я буду напоминать тебе каждый день в 15:00.")
    logger.info(f"💾 Сохранён chat_id: {chat_id}")

async def on_startup(application):
    """Запускается при старте приложения — настраивает расписание."""
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(
        send_reminder,
        CronTrigger(hour=REMINDER_TIME_HOUR, minute=0),
        args=[application],
        id="daily_reminder",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("📅 Планировщик запущен")

def main():
    """Главная функция — инициализация и запуск."""
    app = ApplicationBuilder().token(TOKEN).post_init(on_startup).build()
    app.add_handler(CommandHandler("start", start))
    logger.info("🤖 Бот запущен и ждёт команду /start.")
    app.run_polling()

if __name__ == "__main__":
    main()
