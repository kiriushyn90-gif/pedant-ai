import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# КЛЮЧИ (Вставь свои!)
TOKEN = "8740450028:AAGsZzWH-LBfKZnv8x9bZaGtckB-_U1Th5o"
AI_KEY = "AIzaSyBQW9qLIbiuEzPKjLUd97inT2dWv-g_xFg"

# Настройка ИИ
genai.configure(api_key=AI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
@app.route('/')
def home(): return "БОТ ПЕДАНТ РАБОТАЕТ"

# Функция обработки сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Отправляем текст пользователя в нейросеть
        chat_response = model.generate_content(update.message.text)
        await update.message.reply_text(chat_response.text)
    except Exception as e:
        print(f"Ошибка ИИ: {e}")
        await update.message.reply_text("Извини, я призадумался. Попробуй еще раз!")

if __name__ == '__main__':
    # Запуск Flask для Render
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    
    # Запуск Телеграм-бота
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Бот запущен и ждет сообщений...")
    application.run_polling(drop_pending_updates=True)
    
