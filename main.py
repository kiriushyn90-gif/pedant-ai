import os
import asyncio
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Ключи из Render
TOKEN = os.environ.get("TELEGRAM_TOKEN")
AI_KEY = os.environ.get("GEMINI_KEY")

# Настройка Gemini
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Веб-сервер для "здоровья" сервиса на Render
app = Flask(__name__)
@app.route('/')
def home(): return "Бот запущен!"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    logger.info(f"!!! СООБЩЕНИЕ ПОЛУЧЕНО: {update.message.text}")
    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Ошибка ИИ: {e}")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

async def main():
    if not TOKEN:
        logger.error("!!! ОШИБКА: TELEGRAM_TOKEN не найден!")
        return

    # Используем только Application (без ручного создания Updater)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    logger.info("--- ПОПЫТКА СТАРТА ПОЛЛИНГА ---")
    async with application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(drop_pending_updates=True)
        logger.info("--- БОТ В СЕТИ И ЖДЕТ СООБЩЕНИЙ ---")
        # Бесконечный цикл, чтобы бот не выключался
        while True:
            await asyncio.sleep(1)

if __name__ == '__main__':
    # Запускаем Flask в отдельном потоке
    threading.Thread(target=run_flask, daemon=True).start()
    # Запускаем основного бота
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        
