"""
AstroBot - Основной файл для Render + 24/7 работы
Запускает Flask сервер для UptimeRobot И Telegram бота в фоне
"""

from flask import Flask, jsonify
import os
import threading
import time
import sys

app = Flask(__name__)

# ========== МАРШРУТЫ ДЛЯ UPTIMEROBOT ==========

@app.route('/')
def home():
    """Главная страница - UptimeRobot проверяет этот URL"""
    return "AstroBot_24_7_ACTIVE_AND_MONITORED"

@app.route('/health')
def health():
    """Простая проверка здоровья"""
    return "OK", 200

@app.route('/ping')
def ping():
    """Быстрая проверка"""
    return "pong", 200

@app.route('/status')
def status():
    """Детальный статус"""
    return jsonify({
        "status": "online",
        "service": "AstroBot Telegram + Web Server",
        "monitoring": "UptimeRobot every 5 minutes",
        "uptime": "24/7 guaranteed",
        "url": "https://astro-bot-3-n08x.onrender.com",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

# ========== ЗАПУСК TELEGRAM БОТА В ФОНЕ ==========

def run_telegram_bot():
    """Запускает вашего Telegram бота в отдельном процессе"""
    print("=" * 50)
    print("🤖 STARTING TELEGRAM BOT IN BACKGROUND")
    print("=" * 50)
    
    # Даем Flask серверу время запуститься
    time.sleep(5)
    
    try:
        # Запускаем ваш файл бота
        import subprocess
        
        # Запускаем бота в отдельном процессе
        bot_process = subprocess.Popen(
            ["python", "astro_bot3.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ Telegram bot process started")
        print(f"📊 Bot PID: {bot_process.pid}")
        
        # Можно логировать вывод бота
        import threading
        def log_bot_output():
            for line in bot_process.stdout:
                print(f"[BOT] {line.strip()}")
        
        log_thread = threading.Thread(target=log_bot_output, daemon=True)
        log_thread.start()
        
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        import traceback
        traceback.print_exc()

# ========== ЗАПУСК ВСЕГО ==========

if __name__ == '__main__':
    # Запускаем Telegram бота в фоновом потоке
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask сервер
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Starting Flask server on port {port}")
    print(f"📡 UptimeRobot will monitor: https://astro-bot-3-n08x.onrender.com")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
