
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

CHAT_ID = os.getenv('CHAT_ID')
if not CHAT_ID:
    raise ValueError("CHAT_ID не найден в переменных окружения")

# Преобразуем CHAT_ID в int
try:
    CHAT_ID = int(CHAT_ID)
except ValueError:
    raise ValueError("CHAT_ID должен быть числом")

print(f"✅ Конфигурация загружена: Бот токен = {BOT_TOKEN[:10]}... , Чат ID = {CHAT_ID}")

# Состояния разговора - ДОБАВЬТЕ HELP_TYPE
FIO, DEPARTMENT, AUDIENCE, HELP_TYPE, PROBLEM, COMMENT = range(6)

# Специалисты (замените на реальные ID и ФИО)
SPECIALISTS = {
    2146356689: "Щетинин Денис",
    2037536360: "Тарабрин Алексей",
    1301458891: "Безруков Михаил",
    1976269852: "Авдеев Александр",
    5177060366: "Осеков Александр",
    1302452744: "Левицкий Роман",  # Ваш реальный ID
 
    # Добавьте сюда ID и ФИО других специалистов
}
SPECIALIST_NAMES = {name: user_id for user_id, name in SPECIALISTS.items()}
