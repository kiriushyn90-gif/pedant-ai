import os
import logging
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import google.generativeai as genai

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ключи из настроек (Railway Variables)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
AI_KEY = os.environ.get("GEMINI_KEY")

# Настройка Gemini
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Веб-сервер для "галочки" хостинга
app = Flask(__name__)
@app.route('/')
def home(): return "Бот в сети"

# Ответ на команду /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я на связи и готов общаться. Напиши мне что-нибудь!")

# Ответ на обычные сообщения
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    logger.info(f"Получено сообщение: {user_text}")

    try:
        # Пытаемся получить ответ от ИИ
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Ошибка Gemini: {e}")
        await update.message.reply_text("Я получил твоё сообщение, но мой 'мозг' (ИИ) выдал ошибку. Проверь GEMINI_KEY.")

def main():
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN не найден!")
        return

    # Собираем приложение
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply))
    
    logger.info("--- ФИНАЛЬНЫЙ ЗАПУСК БОТА ---")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    # Запуск Flask в фоне
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()
    # Запуск бота
    main()
    
