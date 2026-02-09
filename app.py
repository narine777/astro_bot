from flask import Flask, jsonify
import os
import subprocess
import threading

app = Flask(__name__)

# Маршрут для UptimeRobot
@app.route('/')
def home():
    return "AstroBot_SERVER_IS_UP_AND_RUNNING_24_7"

# Запускаем бота СРАЗУ при импорте
print("=" * 50)
print("🚀 STARTING ASTROBOT SERVER")
print("=" * 50)

# Запускаем бота в отдельном процессе
def run_bot():
    print("🤖 Launching Telegram bot...")
    try:
        # Просто запускаем файл бота
        subprocess.Popen(
            ["python", "astro_bot3.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Bot process started")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")

# Запускаем в отдельном потоке
import threading
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
