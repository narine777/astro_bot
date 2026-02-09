"""
Простой тест бота - запускаем только бота без Flask
"""

import os
import sys

print("=" * 50)
print("🤖 TEST: Starting Telegram Bot")
print("=" * 50)

# 1. Проверяем токен
TOKEN = os.getenv('BOT_TOKEN')
print(f"🔑 Token from env: {'SET' if TOKEN else 'NOT SET'}")

# 2. Пытаемся импортировать бота
try:
    from astro_bot3 import main
    print("✅ SUCCESS: Imported astro_bot3")
    
    # 3. Запускаем бота
    print("🚀 Starting bot...")
    main()
    
except ImportError as e:
    print(f"❌ IMPORT ERROR: {e}")
    print("Files in directory:", os.listdir('.'))
except Exception as e:
    print(f"❌ RUNTIME ERROR: {e}")
    import traceback
    traceback.print_exc()
