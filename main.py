from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "СЕРВЕР ЧИСТ И РАБОТАЕТ"

if __name__ == '__main__':
    # Render сам назначит порт, берем его из настроек
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
  
