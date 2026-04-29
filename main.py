import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
genai.configure(api_key=os.environ.get("GEMINI_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
@app.route('/')
def home(): return "Бот работает"

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        try:
            res = model.generate_content(update.message.text)
            await update.message.reply_text(res.text)
        except Exception as e:
            logger.error(f"Ошибка ИИ: {e}")

def main():
    # Используем стабильный метод запуска
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply))
    logger.info("--- БОТ ЗАПУЩЕН ---")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    # Запуск веб-сервера для Render
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port), daemon=True).start()
    main()
