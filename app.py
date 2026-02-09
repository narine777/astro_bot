"""
AstroBot - Telegram бот для астрономии
Размещен на Render.com с UptimeRobot для работы 24/7
"""

from flask import Flask, jsonify
import os
import threading
import time
import sys

# Создаем Flask приложение
app = Flask(__name__)

# ========== МАРШРУТЫ ДЛЯ RENDER И UPTIMEROBOT ==========

@app.route('/')
def home():
    """Главная страница - UptimeRobot ищет этот текст"""
    return "AstroBot_SERVER_IS_UP_AND_RUNNING_24_7"

@app.route('/health')
def health_check():
    """Маршрут для проверки здоровья - возвращает простой OK"""
    return "OK", 200

@app.route('/status')
def status():
    """Детальный статус в JSON формате"""
    return jsonify({
        "status": "running",
        "service": "AstroBot Telegram Bot",
        "uptime_provider": "Render.com + UptimeRobot",
        "monitoring": "24/7 active",
        "url": "https://astro-bot-3-n08x.onrender.com",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "endpoints": {
            "/": "Main page (UptimeRobot check)",
            "/health": "Health check",
            "/status": "Detailed status",
            "/ping": "Simple ping-pong"
        }
    })

@app.route('/ping')
def ping():
    """Простейший эндпоинт для быстрой проверки"""
    return "pong", 200

# ========== ЗАПУСК TELEGRAM БОТА В ФОНЕ ==========

def start_telegram_bot():
    """
    Запускает основного Telegram бота в отдельном потоке
    """
    print("🤖 [INFO] Preparing to start Telegram bot...")
    
    # Даем Flask серверу время запуститься
    time.sleep(3)
    
    try:
        # Добавляем текущую директорию в Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        print(f"📁 [INFO] Current directory: {current_dir}")
        print(f"📁 [INFO] Files in directory: {os.listdir(current_dir)}")
        
        # Пытаемся импортировать и запустить бота
        try:
            # Попытка 1: Импорт из astro_bot3.py
            from astro_bot3 import main as bot_main
            print("✅ [INFO] Successfully imported astro_bot3.main")
            
            # Запускаем бота в отдельном потоке
            def run_bot():
                print("🚀 [INFO] Starting Telegram bot...")
                try:
                    bot_main()
                except Exception as e:
                    print(f"❌ [ERROR] Bot runtime error: {e}")
            
            bot_thread = threading.Thread(target=run_bot, daemon=True)
            bot_thread.start()
            print("✅ [SUCCESS] Telegram bot started in background thread")
            
        except ImportError as e:
            print(f"⚠️ [WARNING] Cannot import from astro_bot3: {e}")
            
            # Попытка 2: Прямой запуск файла
            try:
                import subprocess
                print("🔄 [INFO] Trying to run bot via subprocess...")
                
                bot_process = subprocess.Popen(
                    [sys.executable, "astro_bot3.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print("✅ [INFO] Bot subprocess started")
                
            except Exception as e2:
                print(f"❌ [ERROR] Subprocess failed: {e2}")
                
    except Exception as e:
        print(f"❌ [ERROR] Failed to start bot: {e}")
        print("ℹ️ [INFO] Bot will not be active, but web server works")

# ========== ЗАПУСК СЕРВЕРА ==========

if __name__ == '__main__':
    # Запускаем Telegram бота в фоне (если есть)
    try:
        bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
        bot_thread.start()
        print("👁️ [INFO] Bot starter thread launched")
    except Exception as e:
        print(f"⚠️ [WARNING] Could not start bot thread: {e}")
    
    # Запускаем Flask сервер
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 [STARTUP] Starting AstroBot server on port {port}")
    print(f"🌐 [URL] Server will be available at your Render URL")
    print(f"🔧 [MODE] Production mode")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,  # False для продакшена
        threaded=True  # Поддержка многопоточности
    )
