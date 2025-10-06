
# Клавиатуры и кнопки
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    """Основная клавиатура после регистрации"""
    keyboard = [
        ["📝 Оставить заявку", "📋 Мои заявки"],
        ["❓ FAQ", "📞 Обратная связь"],
        ["🏠 Меню"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_problem_keyboard():
    """Клавиатура с типами проблем"""
    keyboard = [
        ["💻 Компьютер", "🌐 Интернет"],
        ["🖨️ Принтер", "📺 Проектор/Телевизор"],
        ["⚙️ Программное обеспечение", "🎤 Аудио"],
        ["❓ Другое"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def remove_keyboard():
    """Удаление клавиатуры"""
    return ReplyKeyboardRemove()

def get_application_actions_keyboard(application_id):
    """Клавиатура для принятия/отклонения заявки"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Принять", callback_data=f"accept_{application_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{application_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_completion_keyboard(application_id):
    """Клавиатура для завершения заявки"""
    keyboard = [
        [
            InlineKeyboardButton("💬 Завершить с комментарием", callback_data=f"complete_{application_id}")
        ],
        [
            InlineKeyboardButton("✅ Завершить", callback_data=f"complete_simple_{application_id}")
        ],
        [
            InlineKeyboardButton("🔄 Передать другому", callback_data=f"transfer_{application_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
    
def get_specialists_keyboard(application_id):
    """Клавиатура со списком специалистов для передачи заявки"""
    from config import SPECIALISTS
    
    keyboard = []
    for specialist_id, specialist_name in SPECIALISTS.items():
        keyboard.append([
            InlineKeyboardButton(specialist_name, callback_data=f"transfer_to_{specialist_id}_{application_id}")
        ])
    
    # Кнопка отмены
    keyboard.append([
        InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_transfer_{application_id}")
    ])
    
    return InlineKeyboardMarkup(keyboard)

def get_transfer_acceptance_keyboard(application_id):
    """Клавиатура для принятия/отклонения/возврата передачи заявки"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Принять заявку", callback_data=f"transfer_accept_{application_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"transfer_decline_{application_id}")
        ],
        [
            InlineKeyboardButton("🔄 Вернуть заявку", callback_data=f"transfer_return_{application_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_printer_subkeyboard():
    """Подкатегории для проблем с принтером"""
    keyboard = [
        ["🖨️ Замена картриджа", "🖨️ Настройка принтера"],
        ["🖨️ Замятие Бумаги", "🖨️ Проблемы со сканером"],
        ["🖨️ Иные проблемы с принтером", "🔙 Назад к выбору проблемы"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_computer_subkeyboard():
    """Подкатегории для проблем с компьютером"""
    keyboard = [
        ["💻 Не включается", "💻 Иные проблемы с компьютером"],
        ["🔙 Назад к выбору проблемы"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_internet_subkeyboard():
    """Подкатегории для проблем с интернетом"""
    keyboard = [
        ["🌐 Нет подключения", "🌐 Долгая загрузка"],
        ["🌐 Иные проблемы с интернетом", "🔙 Назад к выбору проблемы"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_software_subkeyboard():
    """Подкатегории для проблем с ПО"""
    keyboard = [
        ["⚙️ Установка программы", "⚙️ Настройка программы"],
        ["⚙️ Иные проблемы с ПО", "🔙 Назад к выбору проблемы"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_projector_subkeyboard():
    """Подкатегории для проблем с проектором/телевизором"""
    keyboard = [
        ["📺 Нет изображения", "📺 Нет звука"],
        ["📺 Иные проблемы", "🔙 Назад к выбору проблемы"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_audio_subkeyboard():
    """Подкатегории для проблем с аудио"""
    keyboard = [
        ["🎤 Запись мероприятия", "🎤 Настройка оборудования"],
        ["🎤 Иные проблемы со звуком", "🔙 Назад к выбору проблемы"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_rating_keyboard(application_id):
    """Клавиатура для оценки специалиста"""
    keyboard = []
    
    # Первый ряд: 1-5
    row1 = []
    for i in range(1, 6):
        row1.append(InlineKeyboardButton(f"{i}⭐", callback_data=f"rate_{application_id}_{i}"))
    keyboard.append(row1)
    
    # Второй ряд: 6-10  
    row2 = []
    for i in range(6, 11):
        row2.append(InlineKeyboardButton(f"{i}⭐", callback_data=f"rate_{application_id}_{i}"))
    keyboard.append(row2)
    
    return InlineKeyboardMarkup(keyboard)
def get_help_type_keyboard():
    """Клавиатура для выбора типа помощи"""
    keyboard = [
        ["💻 Дистанционная помощь"],
        ["🔧 Помощь в очной форме"],
        ["🔙 Назад"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)