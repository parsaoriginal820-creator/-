import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

# 1. تنظیمات اولیه
# دریافت توکن از متغیرهای محیطی
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    # این فقط برای تست محلی است. در Vercel توکن باید تنظیم شود.
    logging.error("TELEGRAM_BOT_TOKEN is not set!")

# 2. تعریف توابع
def start_command(update, context):
    """پاسخ به دستور /start"""
    update.message.reply_text('سلام! به ربات فیلم خوش آمدید. برای جستجو، نام فیلم مورد نظر را برای من ارسال کنید.')

def movie_search_handler(update, context):
    """پاسخ به پیام‌های متنی (جستجوی فیلم)"""
    search_query = update.message.text
    # **اینجا منطق جستجوی فیلم شما قرار می‌گیرد** # (مثلاً تماس با APIهای فیلم مانند TMDB یا OMDB)
    
    # فعلاً یک پاسخ ساده می‌دهیم
    response = f"در حال جستجو برای فیلم: {search_query}..."
    update.message.reply_text(response)


# 3. تنظیم Webhook
app = FastAPI()

@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    """دریافت آپدیت‌ها از تلگرام و ارسال به Dispatcher"""
    if not TOKEN:
        return {"status": "error", "message": "Token not configured"}, 500

    body = await request.json()
    
    # تنظیم Bot و Dispatcher
    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher(bot, None, workers=0)
    
    # اضافه کردن Handlerها
    dispatcher.add_handler(CommandHandler("start", start_command))
    # هر پیام متنی که دستور نیست را به movie_search_handler می‌فرستد
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, movie_search_handler))
    
    try:
        # پردازش آپدیت
        update = Update.de_json(body, bot)
        dispatcher.process_update(update)
    except Exception as e:
        logging.error(f"Error processing update: {e}")
        return {"status": "error", "message": str(e)}, 500

    return {"status": "ok"}
