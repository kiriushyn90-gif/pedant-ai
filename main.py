import os
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ВСТАВЬ СВОЙ ТОКЕН НИЖЕ
TOKEN = "8740450028:AAGsZzWH-LBfKZnv8x9bZaGtckB-_U1Th5o"

app = Flask(__name__)

@app.route('/')
def home():
    return "СЕРВЕР РАБОТАЕТ, БОТ НА СВЯЗИ"

# Функция, которая просто повторяет твои слова
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Ты написал: {update.message.text}")

if __name__ == '__main__':
    # Запуск веб-сервера для Render в отдельном потоке
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    
    # Настройка и запуск бота
    print("Бот запускается...")
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    
    application.run_polling(drop_pending_updates=True)
    
