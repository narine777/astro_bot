"""
🚀 AstroBot: Полный справочник по астрономии с решениями задач
🎯 Солнечная система + звезды для олимпиад
Версия 2.1 - исправлена ошибка запуска
"""

import os
import sys
import json
import re
import logging
import signal
import atexit
import time
import threading
from datetime import datetime

# Telegram импорты
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters
)

# ==================== НАСТРОЙКА ЛОГИРОВАНИЯ ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота из переменных окружения
TOKEN = os.getenv("TOKEN", "8591960754:AAGBlsOx7h28a-UQvSH_0L4u81VMYTsLaFQ")

# ==================== ФАЙЛОВАЯ БЛОКИРОВКА ====================
def create_file_lock():
    """
    Создает файловую блокировку для предотвращения запуска 
    нескольких экземпляров бота одновременно
    """
    lock_file = "/tmp/astro_bot.lock"
    
    try:
        import fcntl
        lock_fd = open(lock_file, 'w')
        
        try:
            # Пытаемся получить эксклюзивную блокировку
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Сохраняем PID текущего процесса
            lock_fd.write(str(os.getpid()))
            lock_fd.flush()
            logger.info("✅ Файловая блокировка установлена")
            
            # Функция для очистки при завершении
            def cleanup_lock():
                try:
                    fcntl.flock(lock_fd, fcntl.LOCK_UN)
                    lock_fd.close()
                    if os.path.exists(lock_file):
                        os.remove(lock_file)
                    logger.info("🔒 Файловая блокировка снята")
                except:
                    pass
            
            atexit.register(cleanup_lock)
            return True
            
        except (IOError, BlockingIOError):
            lock_fd.close()
            logger.error("❌ Бот уже запущен в другом процессе!")
            return False
            
    except ImportError:
        # На Windows нет fcntl, пропускаем блокировку
        logger.warning("⚠️ Модуль fcntl не доступен (Windows?), пропускаем блокировку")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Не удалось создать lock файл: {e}")
        return True  # Продолжаем работу

# ==================== БАЗА ДАННЫХ НЕБЕСНЫХ ТЕЛ ====================
class CelestialDatabase:
    """Класс для работы с базой данных небесных тел"""

    def __init__(self, json_file='celestial_data.json'):
        self.json_file = json_file
        self.data = {}
        self.load_data()

    def load_data(self):
        """Загрузка данных из JSON файла"""
        try:
            if not os.path.exists(self.json_file):
                logger.warning(f"Файл {self.json_file} не найден, создаем примерные данные")
                self.create_sample_data()
                return

            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            logger.info(f"✅ База данных загружена: {len(self.data)} объектов")

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка в формате JSON: {e}")
            self.data = {}
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            self.data = {}

    def create_sample_data(self):
        """Создание примерных данных"""
        self.data = {
            "Солнце": {
                "emoji": "☀️",
                "name_en": "Sun",
                "type": "Звезда (G2V)",
                "mass": "1.9885×10³⁰ кг",
                "radius": "6.957×10⁸ м",
                "distance": "1 а.е.",
                "period": "25.05 дней (экватор)",
                "luminosity": "3.828×10²⁶ Вт (1 L☉)",
                "temperature": "5772 K",
                "accuracy": "Высокая (данные с космических аппаратов)",
                "sources": "NASA, SOHO, SDO",
                "task": "Определить светимость Солнца",
                "solution": "L = 4πR²σT⁴ = 4×3.1416×(6.957×10⁸)²×5.67×10⁻⁸×5772⁴ ≈ 3.828×10²⁶ Вт"
            },
            "Меркурий": {
                "emoji": "☿",
                "name_en": "Mercury",
                "type": "Планета земной группы",
                "mass": "3.3011×10²³ кг",
                "radius": "2.4397×10⁶ м",
                "distance": "0.3871 а.е.",
                "period": "87.97 дней",
                "temperature": "440 K (средн.)",
                "accuracy": "Высокая (данные MESSENGER)",
                "sources": "NASA, MESSENGER",
                "task": "Рассчитать ускорение свободного падения",
                "solution": "g = GM/R² = 6.674×10⁻¹¹×3.301×10²³/(2.44×10⁶)² ≈ 3.70 м/с²"
            },
            "Венера": {
                "emoji": "♀",
                "name_en": "Venus",
                "type": "Планета земной группы",
                "mass": "4.8675×10²⁴ кг",
                "radius": "6.0518×10⁶ м",
                "distance": "0.7233 а.е.",
                "period": "224.7 дней",
                "temperature": "737 K",
                "accuracy": "Высокая (данные Magellan)",
                "sources": "NASA, ESA, Magellan",
                "task": "Сравнить с Землей по массе",
                "solution": "M_Венеры/M_Земли = 4.8675×10²⁴/5.9722×10²⁴ ≈ 0.815"
            },
            "Земля": {
                "emoji": "🌍",
                "name_en": "Earth",
                "type": "Планета земной группы",
                "mass": "5.9722×10²⁴ кг",
                "radius": "6.371×10⁶ м",
                "distance": "1 а.е.",
                "period": "365.25 дней",
                "temperature": "288 K (средн.)",
                "accuracy": "Очень высокая",
                "sources": "Международные стандарты",
                "task": "Рассчитать первую космическую скорость",
                "solution": "v₁ = √(GM/R) = √(6.674×10⁻¹¹×5.972×10²⁴/6.371×10⁶) ≈ 7.91 км/с"
            },
            "Марс": {
                "emoji": "♂",
                "name_en": "Mars",
                "type": "Планета земной группы",
                "mass": "6.4171×10²³ кг",
                "radius": "3.3895×10⁶ м",
                "distance": "1.5237 а.е.",
                "period": "686.98 дней",
                "temperature": "210 K (средн.)",
                "accuracy": "Высокая (данные орбитальных аппаратов)",
                "sources": "NASA, ESA, Mars Reconnaissance Orbiter",
                "task": "Найти плотность Марса",
                "solution": "ρ = 3M/(4πR³) = 3×6.417×10²³/(4×3.1416×(3.390×10⁶)³) ≈ 3933 кг/м³"
            },
            "Юпитер": {
                "emoji": "♃",
                "name_en": "Jupiter",
                "type": "Газовый гигант",
                "mass": "1.8982×10²⁷ кг",
                "radius": "6.9911×10⁷ м",
                "distance": "5.2038 а.е.",
                "period": "4332.59 дней",
                "temperature": "165 K (уровень 1 бар)",
                "accuracy": "Высокая (данные Juno)",
                "sources": "NASA, Juno, Galileo",
                "task": "Рассчитать ускорение на экваторе",
                "solution": "g = GM/R² = 6.674×10⁻¹¹×1.898×10²⁷/(6.991×10⁷)² ≈ 24.79 м/с²"
            },
            "Сатурн": {
                "emoji": "♄",
                "name_en": "Saturn",
                "type": "Газовый гигант",
                "mass": "5.6834×10²⁶ кг",
                "radius": "5.8232×10⁷ м",
                "distance": "9.5826 а.е.",
                "period": "10759.22 дней",
                "temperature": "134 K (уровень 1 бар)",
                "accuracy": "Высокая (данные Cassini)",
                "sources": "NASA, ESA, Cassini",
                "task": "Определить плотность",
                "solution": "ρ = 3M/(4πR³) = 3×5.683×10²⁶/(4×3.1416×(5.823×10⁷)³) ≈ 687 кг/м³"
            },
            "Уран": {
                "emoji": "♅",
                "name_en": "Uranus",
                "type": "Ледяной гигант",
                "mass": "8.6810×10²⁵ кг",
                "radius": "2.5362×10⁷ м",
                "distance": "19.191 а.е.",
                "period": "30687.15 дней",
                "temperature": "76 K (тропопауза)",
                "accuracy": "Средняя (данные Voyager 2)",
                "sources": "NASA, Voyager 2",
                "task": "Рассчитать первую космическую скорость",
                "solution": "v₁ = √(GM/R) = √(6.674×10⁻¹¹×8.681×10²⁵/2.536×10⁷) ≈ 15.1 км/с"
            },
            "Нептун": {
                "emoji": "♆",
                "name_en": "Neptune",
                "type": "Ледяной гигант",
                "mass": "1.02413×10²⁶ кг",
                "radius": "2.4622×10⁷ м",
                "distance": "30.07 а.е.",
                "period": "60190.03 дней",
                "temperature": "72 K (тропопауза)",
                "accuracy": "Средняя (данные Voyager 2)",
                "sources": "NASA, Voyager 2",
                "task": "Сравнить с Ураном",
                "solution": "M_Нептуна/M_Урана = 1.024×10²⁶/8.681×10²⁵ ≈ 1.18"
            },
            "Сириус": {
                "emoji": "⭐️",
                "name_en": "Sirius",
                "type": "Двойная звезда (A1V + DA2)",
                "mass": "2.02 M☉ (Сириус A)",
                "radius": "1.71 R☉",
                "distance": "2.64 пк (8.6 св. лет)",
                "luminosity": "25.4 L☉",
                "temperature": "9940 K",
                "accuracy": "Высокая (параллакс Hipparcos)",
                "sources": "Hipparcos, Hubble, Gaia",
                "task": "Рассчитать абсолютную звездную величину",
                "solution": "M = m - 5lg(d/10) = -1.46 - 5lg(2.64/10) ≈ +1.42"
            }
        }
        self.save_data()
        logger.info(f"📁 Создан файл {self.json_file} с примерными данными")

    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Данные сохранены в {self.json_file}")
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")

    def parse_scientific_number(self, value_str):
        """Парсинг чисел в научной нотации"""
        if not value_str:
            return None

        try:
            # Удаляем единицы измерения
            value_str = re.sub(r'[^\d×\.eE\+\-^⁰¹²³⁴⁵⁶⁷⁸⁹]', '', value_str)

            # Заменяем символы степени
            superscript_map = {
                '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
                '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'
            }
            for sup, num in superscript_map.items():
                value_str = value_str.replace(sup, num)

            # Заменяем × на *
            value_str = value_str.replace('×', '*')
            value_str = value_str.replace('^', '**')

            return eval(value_str)
        except Exception as e:
            logger.warning(f"Не удалось распарсить число: {value_str}")
            return None

    def calculate_density(self, body_name):
        """Рассчитать плотность небесного тела"""
        body = self.data.get(body_name)
        if not body:
            return None

        try:
            mass = self.parse_scientific_number(body.get('mass', ''))
            radius = self.parse_scientific_number(body.get('radius', ''))

            if mass is None or radius is None:
                return None

            volume = (4 / 3) * 3.1415926535 * (radius ** 3)
            density = mass / volume if volume > 0 else 0

            return {
                'name': body_name,
                'mass_kg': mass,
                'radius_m': radius,
                'volume_m3': volume,
                'density_kg_m3': density,
                'density_g_cm3': density / 1000,
                'formula': 'ρ = 3M/(4πR³)'
            }
        except Exception as e:
            logger.error(f"Ошибка расчета плотности: {e}")
            return None


# Инициализация базы данных
celestial_db = CelestialDatabase('celestial_data.json')
CELESTIAL_DATA = celestial_db.data

# Проверка загрузки данных
if not CELESTIAL_DATA:
    logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось загрузить базу данных!")
    sys.exit(1)

# ==================== KEEP-ALIVE (только для веб-хостов) ====================
def keep_alive():
    """Функция для поддержания активности (опционально)"""
    try:
        import requests
        web_url = os.getenv("WEB_URL", "")
        if web_url:
            while True:
                try:
                    response = requests.get(web_url, timeout=5)
                    logger.info(f"🟢 Ping: {response.status_code}")
                except Exception as e:
                    logger.warning(f"🔴 Ping неудачен: {e}")
                time.sleep(300)  # 5 минут
    except ImportError:
        pass

# ==================== КЛАВИАТУРЫ ====================
def get_main_keyboard():
    """Основная клавиатура"""
    keyboard = [
        [KeyboardButton("🪐 8 Планет"), KeyboardButton("⭐️ Сириус"), KeyboardButton("☀️ Солнце")],
        [KeyboardButton("📊 Сравнить"), KeyboardButton("📝 Задачи"), KeyboardButton("🔬 Методы")],
        [KeyboardButton("❓ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def get_planets_keyboard():
    """Клавиатура с 8 планетами"""
    keyboard = [
        [InlineKeyboardButton("☿ Меркурий", callback_data="body_Меркурий"),
         InlineKeyboardButton("♀ Венера", callback_data="body_Венера")],
        [InlineKeyboardButton("🌍 Земля", callback_data="body_Земля"),
         InlineKeyboardButton("♂ Марс", callback_data="body_Марс")],
        [InlineKeyboardButton("♃ Юпитер", callback_data="body_Юпитер"),
         InlineKeyboardButton("♄ Сатурн", callback_data="body_Сатурн")],
        [InlineKeyboardButton("♅ Уран", callback_data="body_Уран"),
         InlineKeyboardButton("♆ Нептун", callback_data="body_Нептун")],
        [InlineKeyboardButton("🔙 Назад в меню", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_compare_keyboard():
    """Клавиатура для сравнения"""
    keyboard = [
        [InlineKeyboardButton("Земля vs Марс", callback_data="compare_Земля_Марс"),
         InlineKeyboardButton("Венера vs Земля", callback_data="compare_Венера_Земля")],
        [InlineKeyboardButton("Юпитер vs Сатурн", callback_data="compare_Юпитер_Сатурн"),
         InlineKeyboardButton("Солнце vs Сириус", callback_data="compare_Солнце_Сириус")],
        [InlineKeyboardButton("🔙 Назад в меню", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_tasks_keyboard():
    """Клавиатура с задачами"""
    keyboard = [
        [InlineKeyboardButton("📐 Космические скорости", callback_data="task_velocity"),
         InlineKeyboardButton("⚖️ Сравнение масс", callback_data="task_mass")],
        [InlineKeyboardButton("🌍 Сила тяжести", callback_data="task_gravity"),
         InlineKeyboardButton("🔄 Периоды", callback_data="task_period")],
        [InlineKeyboardButton("⭐️ Звездные задачи", callback_data="task_stars")],
        [InlineKeyboardButton("🔙 Назад в меню", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ==================== ОСНОВНЫЕ КОМАНДЫ ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    welcome = """
🚀 *Добро пожаловать в AstroBot!*
*Справочник для олимпиадной астрономии*

*Доступные объекты:*
• ☀️ **Солнце** - наша звезда
• 🪐 **8 Планет** - от Меркурия до Нептуна
• ⭐️ **Сириус** - самая яркая звезда

*Функции:*
📊 **Сравнить** - сравнение двух объектов
📝 **Задачи** - олимпиадные задачи с решениями
🔬 **Методы** - методики измерений
❓ **Помощь** - справка по боту

*Нажмите кнопку ниже для начала:*
"""
    await update.message.reply_text(welcome, parse_mode='Markdown', reply_markup=get_main_keyboard())


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text

    if text == "🪐 8 Планет":
        await update.message.reply_text(
            "🌌 *Выберите планету:*\n(8 планет Солнечной системы)",
            parse_mode='Markdown',
            reply_markup=get_planets_keyboard()
        )

    elif text == "⭐️ Сириус":
        await show_celestial_body_direct(update, "Сириус")

    elif text == "☀️ Солнце":
        await show_celestial_body_direct(update, "Солнце")

    elif text == "📊 Сравнить":
        await update.message.reply_text(
            "⚖️ *Выберите пару для сравнения:*",
            parse_mode='Markdown',
            reply_markup=get_compare_keyboard()
        )

    elif text == "📝 Задачи":
        await update.message.reply_text(
            "📚 *Выберите тип задачи из списка ниже:*",
            parse_mode='Markdown',
            reply_markup=get_tasks_keyboard()
        )

    elif text == "🔬 Методы":
        await show_methods(update)

    elif text == "❓ Помощь":
        await show_help(update)

    elif text.lower().startswith("плотность:"):
        await calculate_density_from_text(update, context, text)

    else:
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки меню ⬇️",
            reply_markup=get_main_keyboard()
        )


# ==================== ФУНКЦИИ ДЛЯ РАБОТЫ С ДАННЫМИ ====================
async def show_celestial_body_direct(update: Update, body_name: str):
    """Показать информацию о небесном теле"""
    if body_name not in CELESTIAL_DATA:
        await update.message.reply_text(
            f"❌ Объект '{body_name}' не найден в базе данных.",
            reply_markup=get_main_keyboard()
        )
        return

    body = CELESTIAL_DATA[body_name]
    await send_body_info(update.message, body_name, body)


async def show_celestial_body_inline(query, body_name: str):
    """Показать информацию через инлайн-кнопку"""
    if body_name not in CELESTIAL_DATA:
        await query.edit_message_text(
            f"❌ Объект '{body_name}' не найден в базе данных.",
            parse_mode='Markdown'
        )
        return

    body = CELESTIAL_DATA[body_name]
    response = format_body_info(body_name, body)

    if body_name in ["Меркурий", "Венера", "Земля", "Марс", "Юпитер", "Сатурн", "Уран", "Нептун"]:
        keyboard = [[InlineKeyboardButton("🔙 Назад к планетам", callback_data="back_planets")]]
    else:
        keyboard = [[InlineKeyboardButton("🔙 Назад в меню", callback_data="back_main")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)


def format_body_info(body_name: str, body: dict) -> str:
    """Форматирование информации о небесном теле"""
    response = f"{body['emoji']} *{body_name.upper()}* ({body['name_en']})\n\n"
    response += f"📌 *Тип:* {body['type']}\n\n"

    response += f"⚖️ *Масса:* {body['mass']}\n"
    response += f"📏 *Радиус:* {body['radius']}\n"

    if 'distance' in body and body['distance']:
        response += f"📍 *Расстояние:* {body['distance']}\n"

    if 'period' in body and body['period']:
        response += f"🔄 *Период обращения:* {body['period']}\n"

    if 'luminosity' in body and body['luminosity']:
        response += f"☀️ *Светимость:* {body['luminosity']}\n"

    if 'temperature' in body and body['temperature']:
        response += f"🌡️ *Температура:* {body['temperature']}\n"

    response += f"\n📊 *Точность:* {body['accuracy']}\n"
    response += f"📚 *Источники:* {body['sources']}\n\n"
    response += f"🎯 *{body['task']}*\n\n"
    response += body['solution']
    response += "\n\n_Используйте данные для решения олимпиадных задач!_"

    return response


async def send_body_info(message, body_name: str, body: dict):
    """Отправка информации о небесном теле"""
    response = format_body_info(body_name, body)
    await message.reply_text(response, parse_mode='Markdown', reply_markup=get_main_keyboard())


# ==================== СРАВНЕНИЕ ====================
async def show_comparison(query, body1: str, body2: str):
    """Показать сравнение"""
    if body1 not in CELESTIAL_DATA or body2 not in CELESTIAL_DATA:
        await query.edit_message_text("❌ Один из объектов не найден в базе данных.")
        return

    b1 = CELESTIAL_DATA[body1]
    b2 = CELESTIAL_DATA[body2]

    response = f"📊 *СРАВНЕНИЕ: {b1['emoji']} {body1} vs {b2['emoji']} {body2}*\n\n"
    response += f"⚖️ *Масса:*\n• {body1}: {b1['mass']}\n• {body2}: {b2['mass']}\n\n"
    response += f"📏 *Радиус:*\n• {body1}: {b1['radius']}\n• {body2}: {b2['radius']}\n\n"

    # Специальные сравнения
    if body1 == "Земля" and body2 == "Марс":
        density1 = celestial_db.calculate_density("Земля")
        density2 = celestial_db.calculate_density("Марс")

        if density1 and density2:
            response += f"📏 *Плотность:*\n"
            response += f"• Земля: {density1['density_kg_m3']:.0f} кг/м³\n"
            response += f"• Марс: {density2['density_kg_m3']:.0f} кг/м³\n"
            response += f"• Отношение: {density1['density_kg_m3'] / density2['density_kg_m3']:.2f}\n\n"

        response += """📝 **Сравнение силы тяжести:**
g_Земля = 9.81 м/с²
g_Марс = 3.71 м/с²
Отношение: g_Марс/g_Земля = 3.71/9.81 ≈ 0.38

📐 **Формула сравнения:** g₁/g₂ = (M₁/M₂) × (R₂²/R₁²)

🎯 **Вывод:** Сила тяжести на Марсе составляет ~38% от земной
"""

    elif body1 == "Венера" and body2 == "Земля":
        density1 = celestial_db.calculate_density("Венера")
        density2 = celestial_db.calculate_density("Земля")

        if density1 and density2:
            response += f"📏 *Плотность:*\n"
            response += f"• Венера: {density1['density_kg_m3']:.0f} кг/м³\n"
            response += f"• Земля: {density2['density_kg_m3']:.0f} кг/м³\n"
            response += f"• Отношение: {density1['density_kg_m3'] / density2['density_kg_m3']:.2f}\n\n"

        response += """📝 **Сравнение силы тяжести:**
g_Венера = 8.87 м/с²
g_Земля = 9.81 м/с²
Отношение: g_Венера/g_Земля = 8.87/9.81 ≈ 0.904

📐 **Формула сравнения:** g = GM/R²

🎯 **Вывод:** Сила тяжести на Венере ~90% от земной, несмотря на близкие размеры
"""

    elif body1 == "Юпитер" and body2 == "Сатурн":
        density1 = celestial_db.calculate_density("Юпитер")
        density2 = celestial_db.calculate_density("Сатурн")

        if density1 and density2:
            response += f"📏 *Плотность:*\n"
            response += f"• Юпитер: {density1['density_kg_m3']:.0f} кг/м³\n"
            response += f"• Сатурн: {density2['density_kg_m3']:.0f} кг/м³\n"
            response += f"• Отношение: {density1['density_kg_m3'] / density2['density_kg_m3']:.2f}\n\n"

        response += """📝 **Сравнение плотности:**
ρ_Юпитер = 1.33 г/см³
ρ_Сатурн = 0.69 г/см³
Отношение: ρ_Юпитер/ρ_Сатурн ≈ 1.93

📐 **Формула:** ρ = 3M/(4πR³)

🎯 **Вывод:** Юпитер почти в 2 раза плотнее Сатурна
"""

    elif body1 == "Солнце" and body2 == "Сириус":
        response += """📝 **Сравнение светимости:**
L_Солнце = 1 L☉
L_Сириус = 25.4 L☉
Отношение: L_Сириус/L_Солнце = 25.4

📐 **Формула:** L ∝ M³·⁵ (зависимость масса-светимость для главной последовательности)

🎯 **Вывод:** Сириус в 25.4 раза ярче Солнца
"""

    keyboard = [[InlineKeyboardButton("🔙 Назад к сравнению", callback_data="back_compare")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)


# ==================== ЗАДАЧИ ====================
async def show_task_with_solution(query, task_type: str):
    """Показать задачу с полным решением"""
    tasks = {
        "velocity": """
🚀 **ЗАДАЧА: Космические скорости Марса**

📝 **Условие:**
Вычислите первую и вторую космические скорости для Марса.

📐 **Формулы:**
1. Первая космическая скорость (круговая орбита):
   v₁ = √(GM/R)
2. Вторая космическая скорость (параболическая):
   v₂ = √(2GM/R) = v₁√2

🔢 **Данные для Марса:**
- G = 6.67430×10⁻¹¹ м³/(кг·с²)
- M_Марс = 6.4171×10²³ кг
- R_Марс = 3.3895×10⁶ м

📝 **Решение:**
1. **Первая космическая скорость:**
   v₁ = √(6.67430×10⁻¹¹ × 6.4171×10²³ / 3.3895×10⁶)
   v₁ = √(1.264×10⁷) ≈ 3.56×10³ м/с

2. **Вторая космическая скорость:**
   v₂ = √(2) × v₁ = 1.414 × 3.56×10³ ≈ 5.03×10³ м/с

🎯 **Ответы:**
- Первая космическая скорость Марса: **~3.56 км/с**
- Вторая космическая скорость Марса: **~5.03 км/с**

📊 **Сравнение с Землей:**
- Земля: v₁ = 7.91 км/с, v₂ = 11.2 км/с
- Марс в 2.2 раза легче удержать на орбите!
""",

        "mass": """
⚖️ **ЗАДАЧА: Сравнение масс планет-гигантов**

📝 **Условие:**
Во сколько раз масса Юпитера больше массы Сатурна?

📐 **Формула сравнения масс:**
N = M₁/M₂

🔢 **Данные:**
- M_Юпитер = 1.8982×10²⁷ кг
- M_Сатурн = 5.6834×10²⁶ кг

📝 **Решение:**
N = M_Юпитер / M_Сатурн
N = 1.8982×10²⁷ / 5.6834×10²⁶
N = 3.339

🎯 **Ответ:**
Юпитер в **3.34 раза** массивнее Сатурна

📊 **Распределение массы в Солнечной системе:**
- Солнце: 99.86%
- Юпитер: 0.10%
- Остальные планеты: 0.04%
""",

        "gravity": """
🌍 **ЗАДАЧА: Сила тяжести на планетах земной группы**

📝 **Условие:**
Рассчитайте ускорение свободного падения на Венере.

📐 **Формула:**
g = GM/R²

🔢 **Данные для Венеры:**
- M_Венера = 4.8675×10²⁴ кг
- R_Венера = 6.0518×10⁶ м
- M_Земля = 5.9722×10²⁴ кг
- R_Земля = 6.371×10⁶ м

📝 **Решение:**
1. **Ускорение на Венере:**
   g_В = (6.67430×10⁻¹¹ × 4.8675×10²⁴) / (6.0518×10⁶)²
   g_В ≈ 8.87 м/с²

2. **Ускорение на Земле:**
   g_З = (6.67430×10⁻¹¹ × 5.9722×10²⁴) / (6.371×10⁶)²
   g_З ≈ 9.82 м/с²

3. **Сравнение:**
   g_В / g_З = 8.87 / 9.82 ≈ 0.903

🎯 **Ответы:**
- Ускорение на Венере: **8.87 м/с²**
- На Земле: **9.82 м/с²**
- Отношение: **~0.90** (90% от земного)
""",

        "period": """
🔄 **ЗАДАЧА: Орбитальные и синодические периоды**

📝 **Условие:** Определите синодический период Венеры.

📐 **Формула:**
1/S = 1/T₁ - 1/T₂

🔢 **Данные:**
- T_Венера = 224.7 дней
- T_Земля = 365.25 дней

📝 **Решение:**
1/S = 1/224.7 - 1/365.25
1/S = 0.004451 - 0.002738 = 0.001713
S = 1/0.001713 ≈ 583.8 дней

🎯 **Ответ:** Синодический период Венеры **~584 дня**

📊 **Таблица периодов (дни):**
- Меркурий: 87.97 (сид.), 115.9 (синод.)
- Венера: 224.7 (сид.), 583.9 (синод.)
- Земля: 365.25
- Марс: 687.0 (сид.), 779.9 (синод.)
""",

        "stars": """
⭐️ **ЗАДАЧА: Звездные характеристики Сириуса**

📝 **Условие:** Во сколько раз Сириус ярче Солнца?

🔢 **Данные:**
- L_Сириус = 25.4 L☉
- L_Солнце = 1 L☉

📝 **Решение:**
N = L_Сириус / L_Солнце = 25.4 / 1 = 25.4

🎯 **Ответ:** Сириус в **25.4 раза** ярче Солнца

📊 **Характеристики Сириуса:**
- Расстояние: 8.6 св. лет
- Температура: 9940 K
- Спектральный класс: A1V
- Возраст: ~200-300 млн лет
"""
    }

    if task_type in tasks:
        response = tasks[task_type]
        response += "\n\n🔍 *Используйте данные из бота для решения своих задач!*"
    else:
        response = "📝 Выберите тип задачи из списка выше"

    keyboard = [[InlineKeyboardButton("🔙 Назад к задачам", callback_data="back_tasks")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)


# ==================== РАСЧЕТ ПЛОТНОСТИ ====================
async def calculate_density_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Рассчитать плотность из текстового сообщения"""
    try:
        text = text.lower()
        if "масса=" in text and "радиус=" in text:
            mass_start = text.find("масса=") + 6
            mass_end = text.find(" ", mass_start)
            if mass_end == -1:
                mass_end = len(text)
            mass_str = text[mass_start:mass_end].replace(",", ".")

            radius_start = text.find("радиус=") + 7
            radius_end = text.find(" ", radius_start)
            if radius_end == -1:
                radius_end = len(text)
            radius_str = text[radius_start:radius_end].replace(",", ".")

            mass = float(mass_str)
            radius = float(radius_str)

            volume = (4 / 3) * 3.1415926535 * (radius ** 3)
            density_kg_m3 = mass / volume
            density_g_cm3 = density_kg_m3 / 1000

            response = f"""
📏 *РЕЗУЛЬТАТ РАСЧЕТА ПЛОТНОСТИ*

*Входные данные:*
• Масса: {mass:.3e} кг
• Радиус: {radius:.3e} м

*📐 Расчет:*
1. Объем: V = (4/3)πR³ = {volume:.3e} м³
2. Плотность: ρ = M/V

*📊 Результаты:*
• Плотность: {density_kg_m3:.2f} кг/м³
• Плотность: {density_g_cm3:.3f} г/см³
"""

            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                "❌ Неверный формат. Используйте:\n"
                "`плотность: масса=5.9722e24 радиус=6.371e6`",
                parse_mode='Markdown'
            )

    except ValueError:
        await update.message.reply_text(
            "❌ Ошибка в формате чисел. Используйте научную нотацию.",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка расчета: {str(e)}",
            parse_mode='Markdown'
        )


# ==================== ОБРАЗОВАТЕЛЬНЫЕ МОДУЛИ ====================
async def show_methods(update: Update):
    """Показать методы измерений"""
    methods = """
🔬 *МЕТОДЫ АСТРОНОМИЧЕСКИХ ИЗМЕРЕНИЙ*

*📡 Определение массы:*
• Планеты: по движению спутников
• Звезды в двойных системах: третий закон Кеплера

*📏 Определение радиуса:*
• Радиолокация (планеты)
• Интерферометрия (звезды)
• Затменные двойные системы

*☀️ Определение светимости:*
• Фотометрия + параллакс
• Модели атмосфер звезд

*📍 Определение расстояния:*
• Тригонометрический параллакс
• Спектроскопический параллакс
• Цефеиды
"""
    await update.message.reply_text(methods, parse_mode='Markdown', reply_markup=get_main_keyboard())


async def show_help(update: Update):
    """Показать помощь"""
    help_text = """
❓ *ПОМОЩЬ ПО ИСПОЛЬЗОВАНИЮ ASTROBOT*

*Основные функции:*
• 🪐 **8 Планет** - информация о планетах
• ⭐️ **Сириус** - данные о звезде
• ☀️ **Солнце** - параметры нашей звезды
• 📊 **Сравнить** - сравнение объектов
• 📝 **Задачи** - олимпиадные задачи
• 🔬 **Методы** - методики измерений

*🎯 Для олимпиад:*
• Все задачи содержат полное решение
• Указаны все используемые формулы
• Приведены промежуточные расчеты

*✅ Особенности:*
• К каждой задаче прилагается решение
• Показаны все шаги расчета
• Формулы указаны в решениях задач
"""
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=get_main_keyboard())


# ==================== ОБРАБОТЧИК КНОПОК ====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на инлайн-кнопки"""
    query = update.callback_query
    await query.answer()

    data = query.data
    logger.info(f"Нажата кнопка: {data}")

    if data.startswith("body_"):
        body_name = data.split("_")[1]
        await show_celestial_body_inline(query, body_name)

    elif data.startswith("compare_"):
        bodies = data.split("_")[1:]
        if len(bodies) == 2:
            await show_comparison(query, bodies[0], bodies[1])

    elif data.startswith("task_"):
        task_type = data.split("_")[1]
        await show_task_with_solution(query, task_type)

    elif data == "back_main":
        await query.edit_message_text(
            "🏠 *Возврат в главное меню*",
            parse_mode='Markdown'
        )
        await query.edit_message_reply_markup(None)
        await query.message.reply_text("Главное меню:", reply_markup=get_main_keyboard())

    elif data == "back_planets":
        await query.edit_message_text(
            "🌌 *Выберите планету:*",
            parse_mode='Markdown',
            reply_markup=get_planets_keyboard()
        )

    elif data == "back_compare":
        await query.edit_message_text(
            "⚖️ *Выберите пару для сравнения:*",
            parse_mode='Markdown',
            reply_markup=get_compare_keyboard()
        )

    elif data == "back_tasks":
        await query.edit_message_text(
            "📚 *Выберите тип задачи:*",
            parse_mode='Markdown',
            reply_markup=get_tasks_keyboard()
        )


# ==================== ГРАЦИОЗНОЕ ЗАВЕРШЕНИЕ ====================
def setup_graceful_shutdown(application):
    """Настройка graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Получен сигнал {signum}, завершаем работу...")
        if application.running:
            application.stop()
            application.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


# ==================== ГЛАВНАЯ ФУНКЦИЯ ====================
def main():
    """Основная функция запуска бота"""
    print("=" * 60)
    print(f"🚀 AstroBot запускается...")
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 PID процесса: {os.getpid()}")
    print(f"📁 База данных: {len(CELESTIAL_DATA)} объектов")
    print("=" * 60)

    # Проверка файловой блокировки
    if not create_file_lock():
        print("❌ Бот уже запущен! Завершаем работу...")
        sys.exit(1)

    try:
        # Создаем приложение с увеличенными таймаутами
        application = (
            Application.builder()
            .token(TOKEN)
            .read_timeout(30)
            .write_timeout(30)
            .connect_timeout(30)
            .build()
        )

        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Настройка graceful shutdown
        setup_graceful_shutdown(application)

        # Определяем режим запуска
        railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
        railway_environment = os.getenv("RAILWAY_ENVIRONMENT", "")
        railway_static_url = os.getenv("RAILWAY_STATIC_URL", "")

        # Используем любой доступный Railway URL
        webhook_url = None
        for url_var in [railway_public_domain, railway_static_url]:
            if url_var and url_var.strip():
                webhook_url = f"https://{url_var.strip()}/webhook"
                break

        if webhook_url and railway_environment:
            # Запуск на Railway с вебхуками
            PORT = int(os.getenv("PORT", 8000))

            print(f"🌐 Запуск на Railway")
            print(f"🔗 Вебхук: {webhook_url}")
            print(f"🔌 Порт: {PORT}")

            # Запуск keep-alive в фоне (опционально)
            web_url = os.getenv("WEB_URL", "")
            if web_url:
                keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
                keep_alive_thread.start()
                print("✅ Keep-alive поток запущен")

            application.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path="webhook",
                webhook_url=webhook_url,
                drop_pending_updates=True
            )
        else:
            # Локальный запуск с polling
            print("🔄 Локальный запуск (режим polling)")
            application.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES,
                timeout=30,
                read_timeout=30,
                write_timeout=30
            )

    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
