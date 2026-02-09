from flask import Flask, jsonify
import os
import threading
import sys

app = Flask(__name__)

# Маршрут для проверки работы
@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "bot": "AstroBot",
        "message": "Сервер работает. Добавьте бота позже."
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Сервер запущен на порту {port}")
    app.run(host='0.0.0.0', port=port)
