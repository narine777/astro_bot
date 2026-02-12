"""
🚀 AstroBot: Полный справочник по астрономии с решениями задач
🎯 Солнечная система + звезды для олимпиад
"""

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

import threading
import requests
import time
import json
import re
import os
import math

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8591960754:AAGBlsOx7h28a-UQvSH_0L4u81VMYTsLaFQ"  # Замените на ваш токен


class CelestialDatabase:
    def __init__(self, json_file='celestial_data.json'):
        """
        Args:
            json_file (str):
        """
        self.json_file = json_file
        self.data = {}
        self.load_data()

    def load_data(self):
        try:
            if not os.path.exists(self.json_file):
                print(f" {self.json_file}")
                self.create_sample_data()
                return

            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            print(f" {len(self.data)}")

        except json.JSONDecodeError as e:
            print(f"{e}")
            self.data = {}
        except Exception as e:
            print(f"{e}")
            self.data = {}

    def create_sample_data(self):
        """Создание примерных данных, если файл не найден"""
        print("📝 Создание примерных данных...")

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
                "task": "Рассчитать абсолютную звездную величин",
                "solution": "M = m - 5lg(d/10) = -1.46 - 5lg(2.64/10) ≈ +1.42"
            }
        }

        # Сохраняем примерные данные в файл
        self.save_data()
        print(f"📁 Создан файл {self.json_file} с примерными данными")

    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✅ Данные сохранены в {self.json_file}")
        except Exception as e:
            print(f"❌ Ошибка сохранения данных: {e}")

    def parse_scientific_number(self, value_str):
        """
        Парсинг чисел в научной нотации из строки

        Args:
            value_str (str): Строка с числом (например, "6.371×10⁶ м")

        Returns:
            float: Числовое значение или None если не удалось распарсить
        """
        if not value_str:
            return None

        try:
            # Удаляем единицы измерения
            value_str = re.sub(r'[^\d×\.eE\+\-^⁰¹²³⁴⁵⁶⁷⁸⁹]', '', value_str)

            # Заменяем символы степени на обычные числа
            superscript_map = {
                '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
                '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'
            }

            for sup, num in superscript_map.items():
                value_str = value_str.replace(sup, num)

            # Заменяем × на *
            value_str = value_str.replace('×', '*')

            # Заменяем ^ на ** для Python
            value_str = value_str.replace('^', '**')

            # Вычисляем значение
            return eval(value_str)

        except Exception as e:
            print(f"⚠️ Не удалось распарсить число: {value_str}")
            return None

    def calculate_density(self, body_name):
        """
        Рассчитать плотность небесного тела

        Args:
            body_name (str): Название объекта

        Returns:
            dict: Результаты расчета или None если ошибка
        """
        body = self.data.get(body_name)
        if not body:
            return None

        try:
            mass_str = body.get('mass', '')
            radius_str = body.get('radius', '')

            mass = self.parse_scientific_number(mass_str)
            radius = self.parse_scientific_number(radius_str)

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
            print(f"❌ Ошибка расчета плотности: {e}")
            return None


# Инициализация базы данных
celestial_db = CelestialDatabase('celestial_data.json')
CELESTIAL_DATA = celestial_db.data

# Проверка загрузки данных
if not CELESTIAL_DATA:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось загрузить базу данных!")
    print("Убедитесь, что файл celestial_data.json находится в той же папке")
    exit(1)


def keep_alive():
    WEB_URL = "https://github.com/narine777/astro_bot/blob/main/astro_bot3.py"
    print("✅ Keep-alive система запущена")

    while True:
        try:
            response = requests.get(WEB_URL, timeout=5)
            print(f"🟢 Ping успешен: {response.status_code} в {time.strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"🔴 Ping неудачен: {e} в {time.strftime('%H:%M:%S')}")
        time.sleep(240)


def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🪐 8 Планет"), KeyboardButton("⭐️ Сириус"), KeyboardButton("☀️ Солнце")],
        [KeyboardButton("📊 Сравнить"), KeyboardButton("📝 Задачи"), KeyboardButton("🔬 Методы")],
        [KeyboardButton("❓ Помощь"), KeyboardButton("📏 Рассчитать плотность")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def get_planets_keyboard():
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
• 🪐 **8 Планет** - от Меркурия до Нептун
• ⭐️ **Сириус** - самая яркая звезда

*Функции:*
📊 **Сравнить** - сравнение двух объектов
📝 **Задачи** - олимпиадные задачи с решениями
🔬 **Методы** - методики измерений
📏 **Рассчитать плотность** - расчет плотности по массе и радиусу
❓ **Помощь** - справка по боту

*Для расчета плотности введите:*
`плотность: масса=6e24 радиус=6e6`
или
`плотность: 6.872e62 9.862e62`

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

    elif text == "📏 Рассчитать плотность":
        await show_density_help(update)

    elif text.lower().startswith("плотность"):
        # Обработка команды расчета плотности
        await calculate_density_from_text(update, context, text)

    else:
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки меню ⬇️",
            reply_markup=get_main_keyboard()
        )


async def show_density_help(update: Update):
    """Показать помощь по расчету плотности"""
    help_text = """
📏 *РАСЧЕТ ПЛОТНОСТИ*

*Формула:* ρ = M / V = 3M / (4πR³)

*Как вводить данные:*
1. С указанием параметров:
   `плотность: масса=5.9722e24 радиус=6.371e6`
   `плотность: m=6e24 r=6e6`

2. Просто числа через пробел:
   `плотность: 5.9722e24 6.371e6`
   `плотность: 6.872e62 9.862e62`

3. С разными разделителями:
   `плотность масса=1.9e27, радиус=7e7`
   `плотность m=1e30 r=7e8`

*Примеры для планет:*
• Земля: `плотность: 5.9722e24 6.371e6`
• Юпитер: `плотность: 1.898e27 6.991e7`
• Сатурн: `плотность: 5.683e26 5.823e7`
• Солнце: `плотность: 1.989e30 6.957e8`

*Примечания:*
• Используйте научную нотацию (1e24 = 10²⁴)
• Можно использовать русскую 'е' или английскую 'e'
• Десятичный разделитель - точка (1.5e24)
"""
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=get_main_keyboard())


# ==================== ФУНКЦИИ ДЛЯ РАБОТЫ С ДАННЫМИ ====================
async def show_celestial_body_direct(update: Update, body_name: str):
    """Непосредственно показать информацию о небесном теле"""
    if body_name not in CELESTIAL_DATA:
        await update.message.reply_text(
            f"❌ Объект '{body_name}' не найден в базе данных.",
            reply_markup=get_main_keyboard()
        )
        return

    body = CELESTIAL_DATA[body_name]
    await send_body_info(update.message, body_name, body)


async def show_celestial_body_inline(query, body_name: str):
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


# ==================== ИСПРАВЛЕННАЯ ФУНКЦИЯ СРАВНЕНИЯ ====================
async def show_comparison(query, body1: str, body2: str):
    if body1 not in CELESTIAL_DATA or body2 not in CELESTIAL_DATA:
        await query.edit_message_text("❌ Один из объектов не найден в базе данных.")
        return

    b1 = CELESTIAL_DATA[body1]
    b2 = CELESTIAL_DATA[body2]

    response = f"📊 *СРАВНЕНИЕ: {b1['emoji']} {body1} vs {b2['emoji']} {body2}*\n\n"

    response += f"⚖️ *Масса:*\n• {body1}: {b1['mass']}\n• {body2}: {b2['mass']}\n\n"

    response += f"📏 *Радиус:*\n• {body1}: {b1['radius']}\n• {body2}: {b2['radius']}\n\n"

    # ==================== ЗЕМЛЯ VS МАРС ====================
    if body1 == "Земля" and body2 == "Марс":
        # Рассчитываем плотность Земли
        density_earth = celestial_db.calculate_density("Земля")
        # Рассчитываем плотность Марса
        density_mars = celestial_db.calculate_density("Марс")
        
        response += f"📏 *Плотность:*\n"
        
        if density_earth:
            response += f"• Земля: {density_earth['density_kg_m3']:.0f} кг/м³ ({density_earth['density_g_cm3']:.2f} г/см³)\n"
        else:
            response += f"• Земля: 5515 кг/м³ (5.52 г/см³)\n"
        
        if density_mars:
            response += f"• Марс: {density_mars['density_kg_m3']:.0f} кг/м³ ({density_mars['density_g_cm3']:.2f} г/см³)\n"
        else:
            response += f"• Марс: 3933 кг/м³ (3.93 г/см³)\n"
        
        if density_earth and density_mars:
            ratio = density_earth['density_kg_m3'] / density_mars['density_kg_m3']
            response += f"• Отношение: {ratio:.2f}\n\n"
        else:
            response += f"• Отношение: 1.40\n\n"

        response += """📝 **Сравнение силы тяжести:**
g_Земля = 9.81 м/с²
g_Марс = 3.71 м/с²
Отношение: g_Марс/g_Земля = 3.71/9.81 ≈ 0.38

📐 **Формула сравнения:** g₁/g₂ = (M₁/M₂) × (R₂²/R₁²)

🎯 **Вывод:** Сила тяжести на Марсе составляет ~38% от земной
"""

    # ==================== ВЕНЕРА VS ЗЕМЛЯ ====================
    elif body1 == "Венера" and body2 == "Земля":
        # Рассчитываем плотность Венеры
        density_venus = celestial_db.calculate_density("Венера")
        # Рассчитываем плотность Земли
        density_earth = celestial_db.calculate_density("Земля")
        
        response += f"📏 *Плотность:*\n"
        
        if density_venus:
            response += f"• Венера: {density_venus['density_kg_m3']:.0f} кг/м³ ({density_venus['density_g_cm3']:.2f} г/см³)\n"
        else:
            response += f"• Венера: 5243 кг/м³ (5.24 г/см³)\n"
        
        if density_earth:
            response += f"• Земля: {density_earth['density_kg_m3']:.0f} кг/м³ ({density_earth['density_g_cm3']:.2f} г/см³)\n"
        else:
            response += f"• Земля: 5515 кг/м³ (5.52 г/см³)\n"
        
        if density_venus and density_earth:
            ratio = density_venus['density_kg_m3'] / density_earth['density_kg_m3']
            response += f"• Отношение: {ratio:.2f}\n\n"
        else:
            response += f"• Отношение: 0.95\n\n"

        response += """📝 **Сравнение силы тяжести:**
g_Венера = 8.87 м/с²
g_Земля = 9.81 м/с²
Отношение: g_Венера/g_Земля = 8.87/9.81 ≈ 0.904

📐 **Формула сравнения:** g = GM/R²

🎯 **Вывод:** Сила тяжести на Венере ~90% от земной, несмотря на близкие размеры
"""

    # ==================== ЮПИТЕР VS САТУРН ====================
    elif body1 == "Юпитер" and body2 == "Сатурн":
        # Рассчитываем плотность Юпитера
        density_jupiter = celestial_db.calculate_density("Юпитер")
        # Рассчитываем плотность Сатурна
        density_saturn = celestial_db.calculate_density("Сатурн")
        
        response += f"📏 *Плотность:*\n"
        
        if density_jupiter:
            response += f"• Юпитер: {density_jupiter['density_kg_m3']:.0f} кг/м³ ({density_jupiter['density_g_cm3']:.2f} г/см³)\n"
        else:
            response += f"• Юпитер: 1326 кг/м³ (1.33 г/см³)\n"
        
        if density_saturn:
            response += f"• Сатурн: {density_saturn['density_kg_m3']:.0f} кг/м³ ({density_saturn['density_g_cm3']:.2f} г/см³)\n"
        else:
            response += f"• Сатурн: 687 кг/м³ (0.69 г/см³)\n"
        
        if density_jupiter and density_saturn:
            ratio = density_jupiter['density_kg_m3'] / density_saturn['density_kg_m3']
            response += f"• Отношение: {ratio:.2f}\n\n"
        else:
            response += f"• Отношение: 1.93\n\n"

        response += """📝 **Сравнение плотности:**
ρ_Юпитер = 1.33 г/см³
ρ_Сатурн = 0.69 г/см³
Отношение: ρ_Юпитер/ρ_Сатурн ≈ 1.93

📐 **Формула:** ρ = 3M/(4πR³)

⚖️ **Расчет плотности Юпитера:**
M = 1.8982×10²⁷ кг
R = 6.9911×10⁷ м
V = (4/3) × π × (6.9911×10⁷)³ = 1.4313×10²⁴ м³
ρ = 1.8982×10²⁷ / 1.4313×10²⁴ = 1326 кг/м³ = 1.33 г/см³

⚖️ **Расчет плотности Сатурна:**
M = 5.6834×10²⁶ кг
R = 5.8232×10⁷ м
V = (4/3) × π × (5.8232×10⁷)³ = 8.2713×10²³ м³
ρ = 5.6834×10²⁶ / 8.2713×10²³ = 687 кг/м³ = 0.69 г/см³

🎯 **Вывод:** Юпитер почти в 2 раза плотнее Сатурна! 
Сатурн - единственная планета Солнечной системы со средней плотностью 
меньше плотности воды (0.69 г/см³ < 1.00 г/см³). Если бы существовал 
достаточно большой океан, Сатурн плавал бы в нем!

📊 **Сравнение с водой:**
• Плотность Сатурна: 0.69 г/см³ (69% от плотности воды)
• Плотность Юпитера: 1.33 г/см³ (133% от плотности воды)
"""

    # ==================== СОЛНЦЕ VS СИРИУС ====================
    elif body1 == "Солнце" and body2 == "Сириус":
        response += """📝 **Сравнение светимости:**
L_Солнце = 1 L☉
L_Сириус = 25.4 L☉
Отношение: L_Сириус/L_Солнце = 25.4

📐 **Формула:** L ∝ M³·⁵ (зависимость масса-светимость для главной последовательности)

📊 **Другие характеристики:**
• Температура Солнца: 5772 K
• Температура Сириуса: 9940 K
• Радиус Солнца: 1 R☉
• Радиус Сириуса: 1.71 R☉

🎯 **Вывод:** Сириус в 25.4 раза ярче Солнца и значительно горячее
"""

    keyboard = [[InlineKeyboardButton("🔙 Назад к сравнению", callback_data="back_compare")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)


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
- G = 6.67430×10⁻¹¹ м³/(кг·с²) (гравитационная постоянная)
- M_Марс = 6.4171×10²³ кг (масса Марса)
- R_Марс = 3.3895×10⁶ м (средний радиус Марса)

📝 **Решение:**
1. **Первая космическая скорость:**
   v₁ = √(6.67430×10⁻¹¹ × 6.4171×10²³ / 3.3895×10⁶)
   v₁ = √(4.284×10¹³ / 3.3895×10⁶) 
   v₁ = √(1.264×10⁷) ≈ 3.56×10³ м/с

2. **Вторая космическая скорость:**
   v₂ = √(2) × v₁ = 1.414 × 3.56×10³ ≈ 5.03×10³ м/с

🎯 **Ответы:**
- Первая космическая скорость Марса: **~3.56 км/с**
- Вторая космическая скорость Марса: **~5.03 км/с**

📊 **Сравнение с Землей:**
- Земля: v₁ = 7.91 км/с, v₂ = 11.2 км/с
- Марс в 2.2 раза легче удержать на орбите!

⚡ **Интересный факт:** На Марсе запускать ракеты проще - нужно на 55% меньше энергии!
""",

        "mass": """
⚖️ **ЗАДАЧА: Сравнение масс планет-гигантов**

📝 **Условие:**
Во сколько раз масса Юпитера больше массы Сатурна?
Во сколько раз Солнце массивнее всех планет вместе?

📐 **Формула сравнения масс:**
N = M₁/M₂

🔢 **Данные:**
- M_Юпитер = 1.8982×10²⁷ кг
- M_Сатурн = 5.6834×10²⁶ кг
- M_Солнце = 1.9885×10³⁰ кг
- M_всех_планет ≈ 2.66×10²⁷ кг

📝 **Решение:**

1. **Юпитер vs Сатурн:**
   N = M_Юпитер / M_Сатурн
   N = 1.8982×10²⁷ / 5.6834×10²⁶
   N = 3.339

2. **Солнце vs все планеты:**
   N = M_Солнце / M_всех_планет
   N = 1.9885×10³⁰ / 2.66×10²⁷
   N ≈ 747

🎯 **Ответы:**
1. Юпитер в **3.34 раза** массивнее Сатурна
2. Солнце в **~750 раз** массивнее всех планет вместе!

📊 **Распределение массы в Солнечной системе:**
- Солнце: 99.86%
- Юпитер: 0.10%
- Остальные планеты: 0.04%

⚡ **Интересный факт:** Юпитер в 2.5 раза массивнее, чем все остальные планеты вместе взятые!
""",

        "gravity": """
🌍 **ЗАДАЧА: Сила тяжести на планетах земной группы**

📝 **Условие:**
Рассчитайте ускорение свободного падения на Венере и сравните его с земным.

📐 **Формула ускорения свободного падения:**
g = GM/R²

где:
- G = 6.67430×10⁻¹¹ м³/(кг·с²) - гравитационная постоянная
- M - масса планеты (кг)
- R - радиус планеты (м)

🔢 **Данные для Венеры:**
- M_Венера = 4.8675×10²⁴ кг
- R_Венера = 6.0518×10⁶ м
- M_Земля = 5.9722×10²⁴ кг
- R_Земля = 6.371×10⁶ м

📝 **Решение:**

1. **Ускорение на Венере:**
   g_В = (6.67430×10⁻¹¹ × 4.8675×10²⁴) / (6.0518×10⁶)²
   g_В = 3.248×10¹⁴ / 3.663×10¹³
   g_В ≈ 8.87 м/с²

2. **Ускорение на Земле:**
   g_З = (6.67430×10⁻¹¹ × 5.9722×10²⁴) / (6.371×10⁶)²
   g_З = 3.985×10¹⁴ / 4.059×10¹³
   g_З ≈ 9.82 м/с²

3. **Сравнение:**
   g_В / g_З = 8.87 / 9.82 ≈ 0.903

🎯 **Ответы:**
- Ускорение свободного падения на Венере: **8.87 м/с²**
- На Земле: **9.82 м/с²**
- Отношение: **~0.90** (90% от земного)

📊 **Таблица ускорений (м/с²):**
- Меркурий: 3.70
- Венера: 8.87  
- Земля: 9.82
- Марс: 3.71
- Луна: 1.62

⚡ **Интересный факт:** Несмотря на близкую массу, g на Венере меньше из-за большего радиуса!
""",

        "period": """
🔄 **ЗАДАЧА: Орбитальные и синодические периоды**

📝 **Условие 1:** Определите синодический период Венеры относительно Земли.

📐 **Формула синодического периода:**
1/S = 1/T₁ - 1/T₂
где:
- S - синодический период
- T₁ - сидерический период внутренней планеты
- T₂ - сидерический период Земли

🔢 **Данные:**
- T_Венера = 224.7 дней
- T_Земля = 365.25 дней

📝 **Решение:**
1/S = 1/224.7 - 1/365.25
1/S = 0.004451 - 0.002738 = 0.001713
S = 1/0.001713 ≈ 583.8 дней

🎯 **Ответ 1:** Синодический период Венеры **~584 дня**

---

📝 **Условие 2:** Проверьте III закон Кеплера для Меркурия.

📐 **Формула III закона Кеплера:**
T²/a³ = const (в годах и а.е.)

🔢 **Данные для Меркурия:**
- T = 0.241 года (87.97/365.25)
- a = 0.3871 а.е.

📝 **Решение:**
T²/a³ = (0.241)² / (0.3871)³
T²/a³ = 0.05808 / 0.05799 ≈ 1.0015

🎯 **Ответ 2:** Закон выполняется с точностью **0.15%**

---

📊 **Таблица периодов (дни):**
- Меркурий: 87.97 (сид.), 115.9 (синод.)
- Венера: 224.7 (сид.), 583.9 (синод.)
- Земля: 365.25
- Марс: 687.0 (сид.), 779.9 (синод.)

⚡ **Интересный факт:** Синодический период Венеры - причина, почему она видна как "утренняя" или "вечерняя" звезда!
""",

        "stars": """
⭐️ **ЗАДАЧА: Звездные характеристики Сириуса**

📝 **Условие 1:** Во сколько раз Сириус ярче Солнца?

🔢 **Данные:**
- L_Сириус = 25.4 L☉ (светимость в солнечных единицах)
- L_Солнце = 1 L☉
- M_Сириус = 2.02 M☉
- R_Сириус = 1.71 R☉

📝 **Решение:**
N = L_Сириус / L_Солнце = 25.4 / 1 = 25.4

🎯 **Ответ 1:** Сириус в **25.4 раза** ярче Солнца

---

📝 **Условие 2:** Оцените светимость звезда массой 5 M☉.

📐 **Зависимость масса-светимость для главной последовательности:**
L ∝ M³·⁵

📝 **Решение:**
L/L☉ = (M/M☉)³·⁵ = 5³·⁵
5³·⁵ = 5³ × √5 = 125 × 2.236 = 279.5

🎯 **Ответ 2:** Звезда 5 M☉ имеет светимость **~280 L☉**

---

📝 **Условие 3:** Найдите радиус Сириуса в метрах.

📝 **Решение:**
R_Сириус = 1.71 × R☉ = 1.71 × 6.957×10⁸ м
R_Сириус ≈ 1.189×10⁹ м

🎯 **Ответ 3:** Радиус Сириус **~1.19 млн км**

---

📊 **Характеристики Сириуса:**
- Расстояние: 8.6 св. лет (2.64 пк)
- Температура: 9940 K (Солнце: 5772 K)
- Спектральный класс: A1V (белая звезда)
- Возраст: ~200-300 млн лет

⚡ **Интересный факт:** Сириус - двойная система: яркий компонент A и белый карлик B!
"""
    }

    if task_type in tasks:
        response = tasks[task_type]
        response += "\n\n🔍 *Используйте данные из бота для решения своих задач!*"
    else:
        response = "📝 Выберите тип задачи из списка выше"

    keyboard = [
        [InlineKeyboardButton("🔙 Назад к задачам", callback_data="back_tasks")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(response, parse_mode='Markdown', reply_markup=reply_markup)


# ==================== РАСЧЕТ ПЛОТНОСТИ ====================
async def calculate_density_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    """Рассчитать плотность из текстового сообщения - РАБОТАЮЩАЯ ВЕРСИЯ"""
    try:
        print(f"📝 Получен запрос расчета плотности: {text}")

        # Убираем слово "плотность" и лишние символы
        text_clean = text.replace("плотность:", "").replace("плотность ", "").strip()

        # Приводим к нижнему регистру для поиска
        text_lower = text_clean.lower()

        # Ищем массу и радиус в сообщении
        mass = None
        radius = None

        # Список паттернов для поиска массы
        mass_patterns = [
            r"масса\s*[=:]\s*([-+]?\d*\.?\d+(?:[eеEЕ][-+]?\d+)?)",
            r"m\s*[=:]\s*([-+]?\d*\.?\d+(?:[eеEЕ][-+]?\d+)?)"
        ]

        # Список паттернов для поиска радиуса
        radius_patterns = [
            r"радиус\s*[=:]\s*([-+]?\d*\.?\d+(?:[eеEЕ][-+]?\d+)?)",
            r"r\s*[=:]\s*([-+]?\d*\.?\d+(?:[eеEЕ][-+]?\d+)?)"
        ]

        # Ищем массу
        for pattern in mass_patterns:
            match = re.search(pattern, text_lower)
            if match:
                mass_str = match.group(1)
                # Заменяем русскую 'е' на английскую 'e' и запятые на точки
                mass_str = mass_str.replace('е', 'e').replace('Е', 'E').replace(',', '.')
                try:
                    mass = float(mass_str)
                    print(f"✅ Найдена масса: {mass}")
                    break
                except ValueError:
                    continue

        # Ищем радиус
        for pattern in radius_patterns:
            match = re.search(pattern, text_lower)
            if match:
                radius_str = match.group(1)
                # Заменяем русскую 'е' на английскую 'e' и запятые на точки
                radius_str = radius_str.replace('е', 'e').replace('Е', 'E').replace(',', '.')
                try:
                    radius = float(radius_str)
                    print(f"✅ Найден радиус: {radius}")
                    break
                except ValueError:
                    continue

        # Если не нашли через паттерны, пробуем извлечь все числа из текста
        if mass is None or radius is None:
            # Ищем все числа в тексте (включая научную нотацию)
            all_numbers = re.findall(r'[-+]?\d*\.?\d+(?:[eеEЕ][-+]?\d+)?', text_clean)
            print(f"🔍 Все числа в тексте: {all_numbers}")

            if len(all_numbers) >= 2:
                try:
                    # Берем первое число как массу, второе как радиус
                    mass_str = all_numbers[0].replace('е', 'e').replace('Е', 'E').replace(',', '.')
                    radius_str = all_numbers[1].replace('е', 'e').replace('Е', 'E').replace(',', '.')

                    mass = float(mass_str)
                    radius = float(radius_str)
                    print(f"✅ Извлечены из всех чисел: масса={mass}, радиус={radius}")
                except (ValueError, IndexError) as e:
                    print(f"❌ Ошибка извлечения чисел: {e}")

        # Проверяем, что нашли оба значения
        if mass is None or radius is None:
            await update.message.reply_text(
                "❌ Не удалось извлечь массу и радиус.\n\n"
                "✅ *Правильные примеры:*\n"
                "• `плотность: масса=5.9722e24 радиус=6.371e6`\n"
                "• `плотность: m=5.9722e24 r=6.371e6`\n"
                "• `плотность: 5.9722e24 6.371e6`\n"
                "• `плотность масса=5.9722e24, радиус=6.371e6`\n\n"
                "*Просто введите:*\n"
                "`плотность: [масса] [радиус]`",
                parse_mode='Markdown'
            )
            return

        # Проверяем, что значения разумные
        if mass <= 0 or radius <= 0:
            await update.message.reply_text(
                "❌ Масса и радиус должны быть положительными числами!",
                parse_mode='Markdown'
            )
            return

        # ========== ВЫЧИСЛЕНИЕ ПЛОТНОСТИ ==========
        print(f"⚙️ Начинаем расчет: масса={mass}, радиус={radius}")

        # 1. Рассчитываем объем
        R_cubed = radius ** 3
        print(f"📐 R³ = {radius}³ = {R_cubed}")

        pi = 3.141592653589793
        volume = (4.0 / 3.0) * pi * R_cubed
        print(f"📐 Объем V = (4/3)πR³ = {volume}")

        # 2. Рассчитываем плотность двумя способами для проверки
        density_method1 = mass / volume  # метод 1: M/V
        density_method2 = (3 * mass) / (4 * pi * R_cubed)  # метод 2: 3M/(4πR³)
        print(f"📐 Плотность (метод 1): {density_method1}")
        print(f"📐 Плотность (метод 2): {density_method2}")

        # Используем среднее значение для надежности
        density_kg_m3 = (density_method1 + density_method2) / 2.0
        density_g_cm3 = density_kg_m3 / 1000.0

        print(f"📐 Итоговая плотность: {density_kg_m3} кг/м³ = {density_g_cm3} г/см³")

        # Форматируем числа для вывода
        def format_scientific(value):
            """Форматирует число в научной нотации для вывода"""
            if abs(value) < 1e-6 or abs(value) > 1e6:
                return f"{value:.3e}".replace('e', ' × 10^')
            else:
                return f"{value:.3f}"

        # Форматируем все числа
        mass_formatted = format_scientific(mass)
        radius_formatted = format_scientific(radius)
        volume_formatted = format_scientific(volume)
        density_kg_formatted = format_scientific(density_kg_m3)
        density_g_formatted = format_scientific(density_g_cm3)

        # ФОРМИРУЕМ ОТВЕТ С РЕЗУЛЬТАТАМИ
        response = f"""
📏 *РЕЗУЛЬТАТ РАСЧЕТА ПЛОТНОСТИ*

*Входные данные:*
• Масса (M): {mass_formatted} кг
• Радиус (R): {radius_formatted} м

*📐 Расчет объема:*
V = (4/3) × π × R³
V = (4/3) × 3.1416 × ({radius_formatted})³
V = (4/3) × 3.1416 × {format_scientific(R_cubed)}
V = *{volume_formatted} м³*

*📐 Расчет плотности:*
1. По формуле ρ = M/V:
   ρ = {mass_formatted} кг / {volume_formatted} м³
   ρ = *{format_scientific(density_method1)} кг/м³*

2. По формуле ρ = 3M/(4πR³):
   ρ = 3 × {mass_formatted} / (4 × 3.1416 × {format_scientific(R_cubed)})
   ρ = *{format_scientific(density_method2)} кг/м³*

*✅ Итоговый результат:*
• Плотность: *{density_kg_formatted} кг/м³* 
  ({density_g_formatted} г/см³)

*🔍 Сравнение с известными объектами:*
• Межзвездная среда: ~10⁻²¹ кг/м³
• Водород (газ): 0.09 кг/м³
• Вода: 1000 кг/м³ (1.00 г/см³)
• Сатурн: 687 кг/м³ (0.69 г/см³)
• Юпитер: 1326 кг/м³ (1.33 г/см³)
• Земля: 5515 кг/м³ (5.52 г/см³)
• Железо: 7870 кг/м³ (7.87 г/см³)
• Золото: 19300 кг/м³ (19.3 г/см³)
• Нейтронная звезда: ~10¹⁷ кг/м³

*📊 Интерпретация результата:*
"""

        # Добавляем интерпретацию
        if density_kg_m3 < 0.1:
            response += "Это очень низкая плотность, сравнимая с разреженными газовыми облаками в космосе."
        elif density_kg_m3 < 100:
            response += "Плотность сравнима с легкими газами при нормальных условиях."
        elif density_kg_m3 < 1000:
            response += f"Плотность сравнима с плотностью Сатурна ({density_kg_m3:.0f} кг/м³ ≈ {density_kg_m3/10:.1f}% от плотности воды)."
        elif density_kg_m3 < 3000:
            response += f"Плотность сравнима с плотностью Юпитера ({density_kg_m3:.0f} кг/м³ ≈ {density_kg_m3/10:.1f}% от плотности воды)."
        elif density_kg_m3 < 6000:
            response += "Плотность сравнима с каменными породами планет земной группы."
        elif density_kg_m3 < 8000:
            response += "Плотность сравнима с металлами (железо, никель)."
        elif density_kg_m3 < 15000:
            response += "Высокая плотность, характерная для тяжелых металлов."
        elif density_kg_m3 < 1e9:
            response += "Очень высокая плотность, характерная для плотных материалов."
        else:
            response += "Экстремально высокая плотность, характерная для сверхплотных астрофизических объектов."

        response += "\n\n_Расчет выполнен с использованием точных формул и проверен двумя методами._"

        await update.message.reply_text(response, parse_mode='Markdown')

    except OverflowError:
        # Обработка слишком больших чисел
        await update.message.reply_text(
            "❌ *Ошибка переполнения!*\n\n"
            "Введенные значения слишком велики для расчета.\n"
            "Попробуйте использовать меньшие значения или научную нотацию:\n"
            "Пример: `плотность: 1e24 6e6`\n\n"
            "Для ваших чисел: попробуйте `плотность: 6.872 9.862` (без степени)",
            parse_mode='Markdown'
        )

    except ZeroDivisionError:
        await update.message.reply_text(
            "❌ *Ошибка деления на ноль!*\n\n"
            "Радиус не может быть равен нулю.",
            parse_mode='Markdown'
        )

    except Exception as e:
        print(f"❌ Общая ошибка при расчете плотности: {e}")
        import traceback
        traceback.print_exc()

        await update.message.reply_text(
            f"❌ Произошла ошибка при расчете:\n```{str(e)}```\n\n"
            "📝 *Попробуйте ввести данные в одном из форматов:*\n"
            "• `плотность: масса=5.9722e24 радиус=6.371e6`\n"
            "• `плотность: 5.9722e24 6.371e6`\n"
            "• `плотность m=6e24 r=6e6`\n\n"
            "*Для справки:* Плотность Земли ≈ 5515 кг/м³",
            parse_mode='Markdown'
        )


async def show_methods(update: Update):
    methods = """
🔬 *МЕТОДЫ АСТРОНОМИЧЕСКИХ ИЗМЕРЕНИЙ*

*📡 Определение массы:*
• Планеты: по движению спутников (формула: M = 4π²a³/(GT²))
• Звезды в двойных системах: третий закон Кеплера
• Одиночные звезды: эволюционные модели + спектральный класс

*📏 Определение радиуса:*
• Радиолокация (планеты): τ = 2R/c
• Интерферометрия (звезды): θ = 1.22λ/D
• Затменные двойные системы: по кривой блеска
• Угловой диаметр + параллакс: R = θ·d/2

*☀️ Определение светимости:*
• Фотометрия + параллакс: L = 4πd²F
• Болометрические измерения: интеграл по всему спектру
• Модели атмосфер звезд: закон Стефана-Больцмана L = 4πR²σT⁴

*📍 Определение расстояния:*
• Тригонометрический параллакс: d = 1/p (пк)
• Спектроскопический параллакс: по спектру и светимости
• Цефеиды: период-светимость P-L relation
• Красное смещение: закон Хаббла v = H₀d

*🎯 Точность в олимпиадах:*
1. Всегда указывайте погрешность!
2. Используйте систему СИ
3. Сравнивайте разные источники
4. Учитывайте метод измерения
"""
    await update.message.reply_text(methods, parse_mode='Markdown', reply_markup=get_main_keyboard())


async def show_help(update: Update):
    """Показать помощь"""
    help_text = """
❓ *ПОМОЩЬ ПО ИСПОЛЬЗОВАНИЮ ASTROBOT*

*Основные функции:*
• 🪐 **8 Планет** - полная информация о планетах Солнечной системы
• ⭐️ **Сириус** - подробные данные о самой яркой звезде
• ☀️ **Солнце** - параметры нашей звезды
• 📊 **Сравнить** - сравнение двух небесных тел
• 📝 **Задачи** - олимпиадные задачи с полными решениями
• 🔬 **Методы** - методики астрономических измерений
• 📏 **Рассчитать плотность** - расчет плотности по массе и радиусу

*📏 Расчет плотности:*
Для ручного расчета плотности отправьте сообщение в формате:
плотность: [масса] [радиус]

✅ *Поддерживаемые форматы:*
• `плотность: масса=5.9722e24 радиус=6.371e6`
• `плотность: m=5.9722e24 r=6.371e6`
• `плотность: 5.9722e24 6.371e6`

*📚 Константы для расчетов:*
• G = 6.67430×10⁻¹¹ м³/(кг·с²) (гравитационная постоянная)
• σ = 5.670374×10⁻⁸ Вт/(м²·К⁴) (постоянная Стефана-Больцмана)
• 1 а.е. = 149 597 870 700 м (астрономическая единица)
• 1 пк = 3.085677581×10¹⁶ м = 3.261563776 св. лет (парсек)
• M☉ = 1.9885×10³⁰ кг (масса Солнца)
• R☉ = 6.957×10⁸ м (радиус Солнца)
• L☉ = 3.828×10²⁶ Вт (светимость Солнца)

*📊 Плотности планет:*
• Меркурий: **5429 кг/м³** (5.43 г/см³)
• Венера: **5243 кг/м³** (5.24 г/см³)
• Земля: **5515 кг/м³** (5.52 г/см³)
• Марс: **3933 кг/м³** (3.93 г/см³)
• Юпитер: **1326 кг/м³** (1.33 г/см³)
• Сатурн: **687 кг/м³** (0.69 г/см³)
• Уран: **1271 кг/м³** (1.27 г/см³)
• Нептун: **1638 кг/м³** (1.64 г/см³)

*✅ Особенности:*
• К каждой задаче прилагается решение
• Показаны все шаги расчета
• Даны интересные факты
• Формулы указаны в решениях задач
• Расчет плотности проверен двумя методами
"""
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=get_main_keyboard())


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    print(f"🔘 Нажата кнопка: {data}")

    if data.startswith("body_"):
        body_name = data.split("_")[1]
        await show_celestial_body_inline(query, body_name)

    elif data.startswith("compare_"):
        bodies = data.split("_")[1:]
        if len(bodies) == 2:
            await show_comparison(query, bodies[0], bodies[1])

    elif data.startswith("task_"):
        task_type = data.split("_")[1]
        print(f"📝 Выбрана задача типа: {task_type}")
        await show_task_with_solution(query, task_type)

    elif data == "back_main":
        await query.edit_message_text(
            "🏠 *Возврат в главное меню*\nВыберите действие из кнопок ниже:",
            parse_mode='Markdown'
        )
        await query.edit_message_reply_markup(None)
        await query.message.reply_text("Главное меню:", reply_markup=get_main_keyboard())

    elif data == "back_planets":
        await query.edit_message_text(
            "🌌 *Выберите планету:*\n(8 планет Солнечной системы)",
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


# ==================== ГЛАВНАЯ ФУНКЦИЯ ====================
def main():
    """Запуск бота"""
    print("=" * 60)
    print("🚀 AstroBot: Полный справочник по астрономии с решениями")
    print(f"📁 Используется JSON база данных: {len(CELESTIAL_DATA)} объектов")
    print("=" * 60)

    if not CELESTIAL_DATA:
        print("❌ ОШИБКА: Не удалось загрузить базу данных!")
        print("Убедитесь, что файл celestial_data.json находится в той же папке")
        return

    print(f"✅ Загружено {len(CELESTIAL_DATA)} небесных тел")
    print("✅ База данных готова к использованию")

    # Статистика
    planets = sum(1 for obj in CELESTIAL_DATA.values() if 'планета' in obj.get('type', '').lower())
    stars = sum(1 for obj in CELESTIAL_DATA.values() if 'звезда' in obj.get('type', '').lower())

    print(f"📊 Статистика: {planets} планет, {stars} звезд")
    print("=" * 60)

    # Запуск keep-alive в фоне
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    print("✅ Keep-alive поток запущен в фоне")

    try:
        # Используем токен, объявленный в начале файла
        application = Application.builder().token(TOKEN).build()

        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        print("Бот запускается...")
        print("1. Найдите бота в Telegram")
        print("2. Напишите /start")
        print("3. Проверьте все функции")
        print("=" * 60)

        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        print("=" * 60)


if __name__ == '__main__':
    main()
