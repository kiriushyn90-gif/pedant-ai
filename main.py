import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# Настройка логирования, чтобы мы видели всё в панели Render
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("8740450028:AAGsZzWH-LBfKZnv8x9bZaGtckB-_U1Th5o")
AI_KEY = os.environ.get("AIzaSyAlx_mFR5A9jto90rTvQmDlFBJ5_bXkqzI")


# Настройка ИИ
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
@app.route('/')
def home():
    return "СЕРВЕР LIVE"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_text = update.message.text
    logger.info(f"ПОЛУЧЕНО: {user_text}") # Увидим это в логах Render
    
    try:
        response = model.generate_content(user_text)
        await update.message.reply_text(response.text)
        logger.info("ОТВЕТ ОТПРАВЛЕН")
    except Exception as e:
        logger.error(f"ОШИБКА ИИ: {e}")
        await update.message.reply_text("Я призадумался, попробуй еще раз!")

def run_bot():
    logger.info("Запуск бота...")
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    # Запускаем бота в фоне
    threading.Thread(target=run_bot, daemon=True).start()
    # Запускаем Flask для Render на основном потоке
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
