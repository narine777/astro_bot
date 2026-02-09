"""
WSGI файл для запуска на Render с gunicorn
"""

from app import app

# Gunicorn ищет переменную 'application' или 'app'
# У нас есть 'app', так что всё ок

if __name__ == "__main__":
    # Локальный запуск для тестов
    app.run(debug=True)
