import os
import asyncio
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Настройка логов
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Берем ключи из переменных окружения
TOKEN = os.environ.get("TELEGRAM_TOKEN")
AI_KEY = os.environ.get("GEMINI_KEY")

# Настройка ИИ
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Настройка веб-сервера для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот активен и слушает!"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    user_text = update.message.text
    logger.info(f"Входящее: {user_text}")
    
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Ошибка ИИ: {e}")
        await update.message.reply_text("Произошла ошибка, попробуй позже.")

async def main_bot():
    # Создаем приложение (новый стандарт библиотеки)
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # Инициализация и запуск
    await application.initialize()
    await application.start()
    logger.info("!!! БОТ УСПЕШНО ЗАПУЩЕН !!!")
    await application.updater.start_polling(drop_pending_updates=True)

def run_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_bot())
    loop.run_forever()

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    threading.Thread(target=run_async_loop, daemon=True).start()
    
    # Запускаем Flask на порту Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
