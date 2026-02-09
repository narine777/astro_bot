from flask import Flask, jsonify, request
import os
import threading
import sys

app = Flask(__name__)

# Импортируем и запускаем ваш бота
def run_telegram_bot():
    """Запускает вашего Telegram бота"""
    try:
        # Добавляем текущую директорию в путь
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Импортируем ваш основной файл бота
        from astro_bot3 import main  # если функция называется main
        # или если бот запускается автоматически при импорте:
        # import astro_bot3
        
        print("🤖 Запускаю Telegram бота...")
        main()  # запускаем функцию main
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Содержимое файлов:")
        print(os.listdir('.'))
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")

# Запускаем бота в фоновом потоке
bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
bot_thread.start()

# Маршруты Flask
@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "bot": "AstroBot",
        "uptime": "24/7 с UptimeRobot",
        "url": "https://astro-bot-3-n08x.onrender.com"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/ping')
def ping():
    return "pong", 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
