import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
AI_KEY = os.environ.get("GEMINI_KEY")

app = Flask(__name__)
@app.route('/')
def home(): return "OK"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если это появится в логах - мы победили связь!
    logger.info(f"!!! СВЯЗЬ ЕСТЬ! ТЕКСТ: {update.message.text}")
    try:
        genai.configure(api_key=AI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Ошибка ИИ: {e}")

def run_bot():
    if not TOKEN:
        logger.error("ОШИБКА: Токен не найден в настройках Render!")
        return
    
    logger.info(f"Запуск бота с токеном, начинающимся на: {TOKEN[:5]}...")
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
