import os
import logging
import datetime
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ---------------- CONFIG ------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS").split(",")))
VIP_GROUP_ID = os.getenv("VIP_GROUP_ID")
MAIN_CHANNEL = os.getenv("MAIN_CHANNEL")
PROMO_CODE = os.getenv("PROMO_CODE")
DATABASE = "bot_data.db"  # Ama PostgreSQL URL haddii aad rabto async PG

# ---------------- LOGGING -----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, is_vip INTEGER DEFAULT 0,
        vip_expiry TEXT, referral_code TEXT, referred_by INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tips (
        id INTEGER PRIMARY KEY AUTOINCREMENT, tip_text TEXT,
        confidence INTEGER, is_vip_tip INTEGER,
        posted_at TEXT, result TEXT DEFAULT 'pending'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, amount REAL, method TEXT,
        proof TEXT, status TEXT DEFAULT 'pending', requested_at TEXT
    )''')
    conn.commit()
    conn.close()

# ---------------- MESSAGES -----------------
WELCOME_MESSAGE = f"👋 Ku soo dhawoow *Somaali Betting Bot*! 🤩\nPromo code: *{PROMO_CODE}*"
VIP_CONGRATS_MESSAGE = "🎉 Hambalyo! Waxaad ku biirtay VIP Group!"
VIP_PRICING_MESSAGE = "💳 Qiimaha VIP:\n- 1 bil: $8\n- 3 bilood: $20\n- 6 bilood: $32"

# ---------------- SCHEDULER ----------------
scheduler = AsyncIOScheduler()

async def scheduled_post(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%H:%M")
    if now == "10:00":
        await context.bot.send_message(chat_id=MAIN_CHANNEL, text="⚽ Wararka iyo saadaasha sports ee maanta (10:00 AM)")
    elif now == "12:00":
        await context.bot.send_message(chat_id=MAIN_CHANNEL, text="🔥 Tips cusub iyo saadaal ciyaaro (12:00 PM)")

# ---------------- HANDLERS -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")
    await update.message.reply_text(VIP_PRICING_MESSAGE, parse_mode="Markdown")

# ---------------- RUN BOT -----------------
if __name__ == "__main__":
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    scheduler.add_job(scheduled_post, "interval", minutes=1, args=[app.bot])
    scheduler.start()

    app.add_handler(CommandHandler("start", start))
    app.run_polling()
