import os
import asyncio
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Логирование
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
AI_KEY = os.environ.get("GEMINI_KEY")

# Настройка Gemini
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Веб-сервер для Render
app = Flask(__name__)
@app.route('/')
def health(): return "Бот в порядке"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    logger.info(f"Получено сообщение: {update.message.text}")
    try:
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Ошибка ИИ: {e}")

async def run_bot():
    # Создаем приложение без использования старого класса Updater напрямую
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    logger.info("!!! ПОДКЛЮЧЕНИЕ К TELEGRAM...")
    # Метод run_polling сам создаст всё нужное внутри
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    # Держим бота запущенным
    while True:
        await asyncio.sleep(1000)

def start_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Запускаем Flask
    threading.Thread(target=start_flask, daemon=True).start()
    
    # Запускаем бота
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass
        
