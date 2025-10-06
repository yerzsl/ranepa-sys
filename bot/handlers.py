
# Обработчики сообщений
import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from config import FIO, DEPARTMENT, AUDIENCE, PROBLEM, CHAT_ID, SPECIALISTS, HELP_TYPE, COMMENT  # Добавьте COMMENT
from database import Database
from keyboards import (
    get_main_keyboard, get_problem_keyboard, remove_keyboard, 
    get_application_actions_keyboard, get_completion_keyboard,
    get_printer_subkeyboard, get_computer_subkeyboard, get_internet_subkeyboard,
    get_software_subkeyboard, get_projector_subkeyboard, get_audio_subkeyboard,
    get_rating_keyboard, get_specialists_keyboard, get_transfer_acceptance_keyboard,
    get_help_type_keyboard
)
from datetime import datetime
from config import FIO, DEPARTMENT, AUDIENCE, PROBLEM, COMMENT, HELP_TYPE  # Здесь COMMENT уже должен быть

logger = logging.getLogger(__name__)
db = Database()

# Словарь для хранения ID сообщений бота, которые нужно удалить
bot_messages_to_delete = {}

async def handle_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка кнопки 'Меню' - показывает главное меню"""
    await start(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start"""
    try:
        user_id = update.message.from_user.id
        
        # Проверяем, зарегистрирован ли пользователь
        user_data = db.get_user(user_id)
        if user_data:
            # Пользователь уже зарегистрирован
            user_name = user_data[1]
            
            welcome_text = (
                "🎓 *Добро пожаловать в RANEPA.SYSTEM!*\n\n"
                f"👋 Рады снова видеть вас, *{user_name}*!\n\n"
                "✨ *Я ваш персональный помощник для:*\n"
                "• Быстрой подачи заявок на техническую поддержку\n"
                "• Отслеживания статуса ваших обращений\n"
                "• Эффективной коммуникации между отделами\n\n"
                "💡 *Что вы можете сделать:*\n"
                "• Сообщить о проблеме с оборудованием\n"
                "• Оставить заявку на устранение неполадок\n"
                "• Запросить помощь с оргтехникой\n"
                "• Получить срочную техническую поддержку\n\n"
                "🚀 *Готовы создать новую заявку?*\n"
                "Просто нажмите кнопку ниже 👇"
            )
            
            # Пытаемся отправить с картинкой для зарегистрированных пользователей
            try:
                with open('def.png', 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=welcome_text,
                        reply_markup=get_main_keyboard(),
                        parse_mode='Markdown'
                    )
                logger.info(f"Приветствие отправлено с картинкой def.png для зарегистрированного пользователя {user_name}")
                
            except FileNotFoundError:
                logger.warning("Файл def.png не найден, отправляем только текст")
                await update.message.reply_text(
                    welcome_text,
                    reply_markup=get_main_keyboard(),
                    parse_mode='Markdown'
                )
                
            except Exception as e:
                logger.warning(f"Ошибка отправки фото def.png: {e}, отправляем только текст")
                await update.message.reply_text(
                    welcome_text,
                    reply_markup=get_main_keyboard(),
                    parse_mode='Markdown'
                )
            
            return ConversationHandler.END
        
        # Если пользователь не зарегистрирован - начинаем регистрацию
        registration_text = (
            "🎓 *Добро пожаловать в RANEPA.SYSTEM!*\n\n"
            "✨ *Умная система технической поддержки* Российской академии народного хозяйства и государственной службы\n\n"
            "🚀 *Преимущества системы:*\n"
            "• ⚡ Мгновенная отправка заявок\n"
            "• 📱 Удобный интерфейс\n"
            "• 🔔 Автоматические уведомления\n"
            "• 📊 Прозрачный статус заявок\n"
            "• 👥 Эффективная работа специалистов\n\n"
            "💼 *Для начала работы нам нужно:*\n"
            "1️⃣ Ваше ФИО - для персонализации и связи\n"
            "2️⃣ Ваш отдел/кафедра - для маршрутизации заявок\n\n"
            "🔒 *Ваши данные защищены* и используются исключительно для работы системы\n\n"
            "📝 *Готовы начать?*\n"
            "Введите ваше *ФИО* полностью:"
        )
        
        sent_message = await update.message.reply_text(
            registration_text,
            reply_markup=remove_keyboard(),
            parse_mode='Markdown'
        )
        
        bot_messages_to_delete[user_id] = [sent_message.message_id]
        return FIO
        
    except Exception as e:
        logger.error(f"Ошибка в start: {e}")
        return ConversationHandler.END

async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка ФИО"""
    try:
        user_id = update.message.from_user.id
        context.user_data['user_name'] = update.message.text
        
        # Удаляем сообщение пользователя и предыдущее сообщение бота
        try:
            await update.message.delete()
            
            if user_id in bot_messages_to_delete:
                for msg_id in bot_messages_to_delete[user_id]:
                    try:
                        await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                    except Exception as e:
                        logger.warning(f"Не удалось удалить сообщение бота: {e}")
                bot_messages_to_delete[user_id] = []
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение: {e}")
        
        # Отправляем новый запрос
        sent_message = await update.message.reply_text(
            "Теперь введите ваш отдел/кафедру:",
            reply_markup=remove_keyboard()
        )
        
        if user_id not in bot_messages_to_delete:
            bot_messages_to_delete[user_id] = []
        bot_messages_to_delete[user_id].append(sent_message.message_id)
        
        return DEPARTMENT
        
    except Exception as e:
        logger.error(f"Ошибка в get_fio: {e}")
        return ConversationHandler.END

async def get_department(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка отдела/кафедры"""
    try:
        user_id = update.message.from_user.id
        user_name = context.user_data['user_name']
        user_info = update.message.text
        
        # Сохраняем пользователя в базу данных
        db.save_user(user_id, user_name, user_info)
        
        # Удаляем сообщение пользователя и предыдущие сообщения бота
        try:
            await update.message.delete()
            
            if user_id in bot_messages_to_delete:
                for msg_id in bot_messages_to_delete[user_id]:
                    try:
                        await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                    except Exception as e:
                        logger.warning(f"Не удалось удалить сообщение бота: {e}")
                bot_messages_to_delete[user_id] = []
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение: {e}")
        
        # Приветственное сообщение после регистрации
        welcome_final_text = (
            f"🎉 *Регистрация завершена!*\n\n"
            f"👋 *Здравствуйте, {user_name}!*\n\n"
            "✨ *Добро пожаловать в команду RANEPA.SYSTEM!*\n\n"
            "🏢 *Ваш профиль:*\n"
            f"• 👤 *ФИО:* {user_name}\n"
            f"• 📍 *Отдел/кафедра:* {user_info}\n\n"
            "🚀 *Теперь вы можете:*\n"
            "• 📨 Создавать заявки на техническую поддержку\n"
            "• 📊 Отслеживать статус выполнения\n"
            "• 🔔 Получать уведомления о прогрессе\n"
            "• ⭐ Оценивать качество обслуживания\n\n"
            "💡 *Система автоматически направит* вашу заявку ответственному специалисту\n\n"
            "📋 *Готовы создать первую заявку?*\n"
            "Нажмите кнопку *«Оставить заявку»* ниже 👇"
        )
        
        # Пытаемся отправить с картинкой
        try:
            with open('def.png', 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=welcome_final_text,
                    reply_markup=get_main_keyboard(),
                    parse_mode='Markdown'
                )
            logger.info(f"Приветственное сообщение отправлено с картинкой def.png для пользователя {user_name}")
            
        except FileNotFoundError:
            logger.warning("Файл def.png не найден, отправляем только текст")
            await update.message.reply_text(
                welcome_final_text,
                reply_markup=get_main_keyboard(),
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.warning(f"Ошибка отправки фото def.png: {e}, отправляем только текст")
            await update.message.reply_text(
                welcome_final_text,
                reply_markup=get_main_keyboard(),
                parse_mode='Markdown'
            )
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Ошибка в get_department: {e}")
        return ConversationHandler.END

async def start_application(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало создания заявки"""
    try:
        user_id = update.message.from_user.id
        
        # Удаляем сообщение с кнопкой
        try:
            await update.message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение: {e}")
        
        sent_message = await update.message.reply_text(
            "В какой аудитории найдена проблема?",
            reply_markup=remove_keyboard()
        )
        
        if user_id not in bot_messages_to_delete:
            bot_messages_to_delete[user_id] = []
        bot_messages_to_delete[user_id].append(sent_message.message_id)
        
        return AUDIENCE
        
    except Exception as e:
        logger.error(f"Ошибка в start_application: {e}")
        return ConversationHandler.END

async def get_audience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка номера аудитории"""
    try:
        user_id = update.message.from_user.id
        context.user_data['audience'] = update.message.text
        
        # Удаляем сообщение пользователя и предыдущее сообщение бота
        try:
            await update.message.delete()
            
            if user_id in bot_messages_to_delete:
                for msg_id in bot_messages_to_delete[user_id]:
                    try:
                        await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                    except Exception as e:
                        logger.warning(f"Не удалось удалить сообщение бота: {e}")
                bot_messages_to_delete[user_id] = []
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение: {e}")
        
        # Запрашиваем тип помощи
        help_type_text = (
            "💡 *Выберите тип помощи:*\n\n"
            "• 💻 *Дистанционная помощь* - специалист поможет удаленно\n"
            "  (настройка ПО, консультация, удаленный доступ)\n\n"
            "• 🔧 *Помощь в очной форме* - специалист приедет в аудиторию\n"
            "  (ремонт оборудования, замена деталей, настройка аппаратуры)\n\n"
            "📝 *Выберите вариант ниже 👇*"
        )
        
        sent_message = await update.message.reply_text(
            help_type_text,
            reply_markup=get_help_type_keyboard(),
            parse_mode='Markdown'
        )
        
        if user_id not in bot_messages_to_delete:
            bot_messages_to_delete[user_id] = []
        bot_messages_to_delete[user_id].append(sent_message.message_id)
        
        return HELP_TYPE
        
    except Exception as e:
        logger.error(f"Ошибка в get_audience: {e}")
        return ConversationHandler.END

async def get_problem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка описания проблемы"""
    try:
        user_id = update.message.from_user.id
        user_message = update.message.text
        
        # Обрабатываем выбор основной категории
        if user_message in ["💻 Компьютер", "🌐 Интернет", "🖨️ Принтер", 
                           "⚙️ Программное обеспечение", "📺 Проектор/Телевизор", 
                           "🎤 Аудио"]:
            
            context.user_data['main_category'] = user_message
            
            # Показываем подкатегории
            if user_message == "🖨️ Принтер":
                subkeyboard = get_printer_subkeyboard()
                sub_text = "🖨️ *Выберите тип проблемы с принтером/сканером:*"
            elif user_message == "💻 Компьютер":
                subkeyboard = get_computer_subkeyboard()
                sub_text = "💻 *Выберите тип проблемы с компьютером:*"
            elif user_message == "🌐 Интернет":
                subkeyboard = get_internet_subkeyboard()
                sub_text = "🌐 *Выберите тип проблемы с интернетом:*"
            elif user_message == "⚙️ Программное обеспечение":
                subkeyboard = get_software_subkeyboard()
                sub_text = "⚙️ *Выберите тип проблемы с ПО:*"
            elif user_message == "📺 Проектор/Телевизор":
                subkeyboard = get_projector_subkeyboard()
                sub_text = "📺 *Выберите тип проблемы с проектором/телевизором:*"
            elif user_message == "🎤 Аудио":
                subkeyboard = get_audio_subkeyboard()
                sub_text = "🎤 *Выберите тип проблемы со звуком:*"
            
            # Удаляем предыдущее сообщение бота
            try:
                if user_id in bot_messages_to_delete:
                    for msg_id in bot_messages_to_delete[user_id]:
                        try:
                            await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                        except Exception as e:
                            logger.warning(f"Не удалось удалить сообщение бота: {e}")
                    bot_messages_to_delete[user_id] = []
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение: {e}")
            
            # Отправляем подкатегории БЕЗ картинки
            sent_message = await update.message.reply_text(
                sub_text,
                reply_markup=subkeyboard,
                parse_mode='Markdown'
            )
            
            bot_messages_to_delete[user_id].append(sent_message.message_id)
            return PROBLEM        
        # Обрабатываем кнопку "Назад"
        elif user_message == "🔙 Назад к выбору проблемы":
            # Удаляем предыдущее сообщение бота
            try:
                if user_id in bot_messages_to_delete:
                    for msg_id in bot_messages_to_delete[user_id]:
                        try:
                            await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                        except Exception as e:
                            logger.warning(f"Не удалось удалить сообщение бота: {e}")
                    bot_messages_to_delete[user_id] = []
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение: {e}")
            
            # Возвращаем к основному выбору
            problem_text = (
                "🔧 *Выберите тип проблемы*\n\n"
                "💡 *Вы можете выбрать один из вариантов ниже:*\n\n"
                "• 💻 *Компьютер* - не включается, иные проблемы\n"
                "• 🌐 *Интернет* - нет подключения, долгая загрузка\n"
                "• 🖨️ *Принтер* - замена картриджа, настройка, замятие, сканер\n"
                "• 📺 *Проектор/Телевизор* - нет изображения, звука\n"
                "• ⚙️ *Программное обеспечение* - установка, настройка программ\n"
                "• 🎤 *Аудио* - запись мероприятий, настройка оборудования\n"
                "• ❓ *Другое* - опишите проблему в свободной форме\n\n"
                "📝 *Выберите вариант ниже 👇*"
            )
            
            sent_message = await update.message.reply_text(
                problem_text,
                reply_markup=get_problem_keyboard(),
                parse_mode='Markdown'
            )
            
            bot_messages_to_delete[user_id].append(sent_message.message_id)
            return PROBLEM
        
        # Обрабатываем выбор "Другое"
        elif user_message == "❓ Другое":
            # Запрашиваем описание проблемы
            sent_message = await update.message.reply_text(
                "✍️ *Опишите вашу проблему подробно:*\n\n"
                "📋 *Что произошло?*\n"
                "📍 *Где находится проблема?*\n"
                "⏰ *Когда началась?*\n\n"
                "💡 *Чем подробнее опишете, тем быстрее мы поможем!*",
                reply_markup=remove_keyboard(),
                parse_mode='Markdown'
            )
            
            bot_messages_to_delete[user_id].append(sent_message.message_id)
            context.user_data['waiting_for_problem_description'] = True
            return PROBLEM
        
        # Если это описание проблемы после выбора "Другое"
        elif context.user_data.get('waiting_for_problem_description'):
            problem = user_message
            context.user_data.pop('waiting_for_problem_description', None)
            return await create_application(update, context, problem)
        
        # Если выбрана подкатегория
        else:
            main_category = context.user_data.get('main_category', '')
            
            if main_category:
                problem = f"{main_category}: {user_message}"
            else:
                problem = user_message
            
            return await create_application(update, context, problem)
        
    except Exception as e:
        logger.error(f"Ошибка в get_problem: {e}")
        return ConversationHandler.END

async def create_application(update: Update, context: ContextTypes.DEFAULT_TYPE, problem: str) -> int:
    """Создание заявки с учетом типа помощи"""
    try:
        user_id = update.message.from_user.id
        audience = context.user_data['audience']
        help_type = context.user_data.get('help_type', '🔧 Помощь в очной форме')  # По умолчанию физическая
        
        logger.info(f"Создание заявки: user_id={user_id}, audience={audience}, help_type={help_type}, problem={problem}")
        
        # Сохраняем заявку в базу данных (нужно обновить метод save_application)
        application_id, user_name, user_department = db.save_application(user_id, audience, problem, help_type)
        
        logger.info(f"Заявка создана: id={application_id}, user_name={user_name}, department={user_department}")
        
        if application_id:
            # Удаляем сообщение пользователя и предыдущие сообщения бота
            try:
                await update.message.delete()
                
                if user_id in bot_messages_to_delete:
                    for msg_id in bot_messages_to_delete[user_id]:
                        try:
                            await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                        except Exception as e:
                            logger.warning(f"Не удалось удалить сообщение бота: {e}")
                    bot_messages_to_delete[user_id] = []
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение: {e}")
            
            # Текст заявки для отправки в группу с указанием типа помощи
            application_text = (
                f"🚨 *НОВАЯ ЗАЯВКА #{application_id}*\n\n"
                f"👤 *От:* {user_name}\n"
                f"🏢 *Отдел:* {user_department}\n"
                f"📍 *Аудитория:* {audience}\n"
                f"📋 *Тип помощи:* {help_type}\n"
                f"📝 *Проблема:* {problem}\n"
                f"🕐 *Время:* {update.message.date.strftime('%d.%m.%Y %H:%M')}\n\n"
                f"⚡ *Требуется срочное решение!*"
            )
            
            try:
                # Пытаемся отправить заявку с картинкой
                with open('new.png', 'rb') as photo:
                    sent_message = await context.bot.send_photo(
                        chat_id=CHAT_ID,
                        photo=photo,
                        caption=application_text,
                        reply_markup=get_application_actions_keyboard(application_id),
                        parse_mode='Markdown'
                    )
                
                context.bot_data[f"application_{application_id}"] = sent_message.message_id
                db.save_application_message_id(application_id, sent_message.message_id)
                
                logger.info(f"Заявка #{application_id} отправлена в чат {CHAT_ID} с message_id {sent_message.message_id}")
                
            except FileNotFoundError:
                logger.warning("Файл new.png не найден, отправляем заявку без картинки")
                sent_message = await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=application_text,
                    reply_markup=get_application_actions_keyboard(application_id),
                    parse_mode='Markdown'
                )
                
                context.bot_data[f"application_{application_id}"] = sent_message.message_id
                db.save_application_message_id(application_id, sent_message.message_id)
                
            except Exception as e:
                logger.warning(f"Ошибка отправки фото new.png: {e}, отправляем заявку без картинки")
                sent_message = await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=application_text,
                    reply_markup=get_application_actions_keyboard(application_id),
                    parse_mode='Markdown'
                )
                
                context.bot_data[f"application_{application_id}"] = sent_message.message_id
                db.save_application_message_id(application_id, sent_message.message_id)
            
            # Подтверждение пользователю с картинкой
            user_confirmation = (
                "✅ *Ваша заявка принята и отправлена ответственному сотруднику!*\n\n"
                f"📋 *Номер заявки:* #{application_id}\n"
                f"📍 *Аудитория:* {audience}\n"
                f"📋 *Тип помощи:* {help_type}\n"
                f"📝 *Проблема:* {problem}\n\n"
                "⏱️ *Ориентировочное время ответа:*\n"
                "• 🟢 Обычно специалисты отвечают в течение 5-15 минут\n\n"
                "🔔 *Вы получите уведомление, когда специалист примет вашу заявку!*"
            )
            
            try:
                with open('zvaccept.png', 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=user_confirmation,
                        reply_markup=get_main_keyboard(),
                        parse_mode='Markdown'
                    )
                logger.info(f"Подтверждение заявки отправлено с картинкой zvaccept.png для заявки #{application_id}")
            except FileNotFoundError:
                logger.warning("Файл zvaccept.png не найден, отправляем только текст")
                await update.message.reply_text(
                    user_confirmation,
                    reply_markup=get_main_keyboard(),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.warning(f"Ошибка отправки фото zvaccept.png: {e}, отправляем только текст")
                await update.message.reply_text(
                    user_confirmation,
                    reply_markup=get_main_keyboard(),
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text(
                "❌ Ошибка при создании заявки. Попробуйте еще раз.",
                reply_markup=get_main_keyboard()
            )
        
        # Очищаем временные данные
        context.user_data.pop('main_category', None)
        context.user_data.pop('waiting_for_problem_description', None)
        context.user_data.pop('help_type', None)
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Ошибка в create_application: {e}")
        return ConversationHandler.END

async def handle_application_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка действий с заявкой (принять/отклонить)"""
    query = update.callback_query
    await query.answer()
    
    try:
        action, application_id = query.data.split('_')
        application_id = int(application_id)
        specialist_id = query.from_user.id
        specialist_name = SPECIALISTS.get(specialist_id, f"Специалист {specialist_id}")
        
        logger.info(f"Обработка действия {action} для заявки #{application_id} специалистом {specialist_name}")
        
        if action == 'accept':
            # Принятие заявки
            success, application_data = db.accept_application(application_id, specialist_id, specialist_name)
            
            if success and application_data:
                user_id = application_data[0] if len(application_data) > 0 else None
                user_name = application_data[1] if len(application_data) > 1 else "Неизвестно"
                user_department = application_data[2] if len(application_data) > 2 else "Неизвестно"
                audience = application_data[3] if len(application_data) > 3 else "Неизвестно"
                problem = application_data[4] if len(application_data) > 4 else "Неизвестно"
                
                # Обновляем сообщение в чате
                application_text = (
                    f"✅ *ПРИНЯТА ЗАЯВКА #{application_id}*\n\n"
                    f"👤 *От:* {user_name}\n"
                    f"🏢 *Отдел:* {user_department}\n"
                    f"📍 *Аудитория:* {audience}\n"
                    f"📝 *Проблема:* {problem}\n"
                    f"🛠️ *Специалист:* {specialist_name}\n"
                    f"⏱️ *Принята:* {query.message.date.strftime('%d.%m.%Y %H:%M')}"
                )
                
                try:
                    await query.edit_message_caption(
                        caption=application_text,
                        reply_markup=get_completion_keyboard(application_id),
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.warning(f"Не удалось редактировать подпись: {e}, редактируем текст")
                    await query.edit_message_text(
                        text=application_text,
                        reply_markup=get_completion_keyboard(application_id),
                        parse_mode='Markdown'
                    )
                
                # Отправляем уведомление пользователю
                if user_id:
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"✅ *Вашу Заявку: #{application_id} Одобрили!*\n\n"
                                 f"🛠️ *Специалист:* {specialist_name}\n"
                                 f"⏱️ *Время принятия:* {query.message.date.strftime('%d.%m.%Y %H:%M')}\n"
                                 f"📍 *Специалист направляется в аудиторию* {audience}\n\n"
                                 f"📞 *По вопросам обращайтесь к назначенному специалисту*",
                            parse_mode='Markdown'
                        )
                        logger.info(f"Уведомление отправлено пользователю {user_id}")
                    except Exception as e:
                        logger.warning(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
                
                # Уведомление в групповом чате
                try:
                    await query.message.reply_text(
                        f"🛠️ *{specialist_name}* принял заявку *#{application_id}* и направляется в аудиторию *{audience}*",
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.warning(f"Не удалось отправить уведомление в группу: {e}")
                
            else:
                await query.answer("Заявка уже обработана другим специалистом", show_alert=True)
                
        elif action == 'reject':
            # Отклонение заявки
            success, application_data = db.reject_application(application_id)
            
            if success and application_data:
                user_id = application_data[0] if len(application_data) > 0 else None
                user_name = application_data[1] if len(application_data) > 1 else "Неизвестно"
                user_department = application_data[2] if len(application_data) > 2 else "Неизвестно"
                audience = application_data[3] if len(application_data) > 3 else "Неизвестно"
                problem = application_data[4] if len(application_data) > 4 else "Неизвестно"
                
                rejected_text = (
                    f"❌ *ОТКЛОНЕНА ЗАЯВКА #{application_id}*\n\n"
                    f"👤 *От:* {user_name}\n"
                    f"🏢 *Отдел:* {user_department}\n"
                    f"📍 *Аудитория:* {audience}\n"
                    f"📝 *Проблема:* {problem}\n"
                    f"🛠️ *Отклонил:* {specialist_name}"
                )
                
                try:
                    await query.edit_message_caption(
                        caption=rejected_text,
                        reply_markup=None,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.warning(f"Не удалось редактировать подпись: {e}, редактируем текст")
                    await query.edit_message_text(
                        text=rejected_text,
                        reply_markup=None,
                        parse_mode='Markdown'
                    )
                
                # Уведомляем пользователя
                if user_id:
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"❌ *Ваша заявка #{application_id} отклонена*\n\n"
                                 f"🛠️ *Специалист:* {specialist_name}\n"
                                 f"💡 *Для уточнения причин обратитесь к специалисту*\n"
                                 f"📞 *Вы можете создать новую заявку с более подробным описанием*",
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.warning(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
                
            else:
                await query.answer("Заявка уже обработана", show_alert=True)
                
        else:
            await query.answer("Неизвестное действие", show_alert=True)
                
    except ValueError as e:
        logger.error(f"Ошибка парсинга callback_data: {e}")
        await query.answer("Ошибка обработки запроса", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка обработки действия с заявкой: {e}")
        await query.answer("Произошла ошибка", show_alert=True)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена операции"""
    try:
        user_id = update.message.from_user.id
        
        context.user_data.pop('waiting_for_problem_description', None)
        
        if user_id in bot_messages_to_delete:
            for msg_id in bot_messages_to_delete[user_id]:
                try:
                    await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                except Exception as e:
                    logger.warning(f"Не удалось удалить сообщение бота: {e}")
            bot_messages_to_delete[user_id] = []
        
        await update.message.reply_text(
            "Операция отменена.",
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Ошибка в cancel: {e}")
        return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка обычных сообщений"""
    try:
        user_id = update.message.from_user.id
        chat_id = update.message.chat_id
        
        # Не показываем клавиатуры в групповых чатах
        if chat_id != user_id:
            return
            
        # Проверяем, зарегистрирован ли пользователь
        user_data = db.get_user(user_id)
        
        if user_data:
            user_name = user_data[1]
            
            help_text = (
                f"👋 *С возвращением, {user_name}!*\n\n"
                "🚀 *RANEPA.SYSTEM к вашим услугам!*\n\n"
                "💡 *Для создания новой заявки:*\n"
                "1. Нажмите кнопку *«📝 Оставить заявку»*\n"
                "2. Укажите аудиторию\n"
                "3. Опишите проблему\n"
                "4. Получите мгновенное подтверждение!\n\n"
                "📊 *Хотите узнать статистику?*\n"
                "Используйте команду /stats\n\n"
                "🛠️ *Готовы к работе?*\n"
                "Нажмите кнопку ниже 👇"
            )
            
            await update.message.reply_text(
                help_text,
                reply_markup=get_main_keyboard(),
                parse_mode='Markdown'
            )
        else:
            unregistered_text = (
                "🎓 *Добро пожаловать в RANEPA.SYSTEM!*\n\n"
                "🔐 *Для доступа к системе требуется регистрация*\n\n"
                "📝 *Это займет всего 2 минуты:*\n"
                "1. Ваше ФИО\n"
                "2. Название отдела/кафедры\n\n"
                "🚀 *Начните работу прямо сейчас!*\n"
                "Введите команду /start"
            )
            
            await update.message.reply_text(
                unregistered_text,
                reply_markup=remove_keyboard(),
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для получения ID чата"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    await update.message.reply_text(
        f"ID этого чата: `{chat_id}`\n"
        f"Ваш ID: `{user_id}`\n"
        f"Добавьте ваш ID в config.py как специалиста",
        parse_mode='MarkdownV2'
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для получения статистики"""
    try:
        user_id = update.message.from_user.id
        
        is_specialist = user_id in SPECIALISTS
        
        today_stats = db.get_today_stats()
        all_time_stats = db.get_all_time_stats()
        wait_stats = db.get_average_waiting_time()
        
        stats_text = "📊 *СТАТИСТИКА СИСТЕМЫ*\n\n"
        
        stats_text += "📅 *ЗА СЕГОДНЯ:*\n"
        stats_text += f"• Всего заявок: {today_stats['total_today']}\n"
        
        status_emojis = {'new': '🆕', 'accepted': '✅', 'completed': '🏁', 'rejected': '❌'}
        for status, count in today_stats['status_stats'].items():
            emoji = status_emojis.get(status, '📋')
            stats_text += f"• {emoji} {status}: {count}\n"
        
        stats_text += "\n⏱️ *ВРЕМЯ ОБСЛУЖИВАНИЯ:*\n"
        if wait_stats['avg_wait_minutes'] > 0:
            stats_text += f"• 🟢 Средний ответ: *{wait_stats['avg_wait_minutes']} мин*\n"
            stats_text += f"• ✅ Среднее решение: *{wait_stats['avg_completion_minutes']} мин*\n"
        else:
            stats_text += "• 📊 Статистика формируется\n"
        
        if today_stats['specialists_today']:
            stats_text += "\n🛠️ *Специалисты сегодня:*\n"
            for specialist, count in today_stats['specialists_today'].items():
                completed = today_stats['completed_today'].get(specialist, 0)
                stats_text += f"• {specialist}: принял {count}, завершил {completed}\n"
        else:
            stats_text += "\n🛠️ Сегодня еще никто не принимал заявок\n"
        
        stats_text += "\n⏳ *ЗА ВСЕ ВРЕМЯ:*\n"
        stats_text += f"• Всего заявок: {all_time_stats['total_all_time']}\n"
        
        for status, count in all_time_stats['status_stats_all'].items():
            emoji = status_emojis.get(status, '📋')
            stats_text += f"• {emoji} {status}: {count}\n"
        
        if all_time_stats['specialists_all']:
            stats_text += "\n🏆 *Топ специалистов:*\n"
            for i, (specialist, count) in enumerate(all_time_stats['specialists_all'].items(), 1):
                completed = all_time_stats['completed_all'].get(specialist, 0)
                stats_text += f"{i}. {specialist}: {count} заявок ({completed} завершено)\n"
        
        if all_time_stats['top_users']:
            stats_text += "\n👥 *Самые активные пользователи:*\n"
            for i, (user_name, department, count) in enumerate(all_time_stats['top_users'], 1):
                stats_text += f"{i}. {user_name} ({department}): {count} заявок\n"
        
        if is_specialist:
            specialist_name = SPECIALISTS[user_id]
            personal_stats = db.get_specialist_stats(specialist_id=user_id)
            stats_text += f"\n👤 *Ваша статистика ({specialist_name}):*\n"
            stats_text += f"• Всего принято: {personal_stats['total']}\n"
            stats_text += f"• Завершено: {personal_stats['completed']}\n"
            stats_text += f"• Принято сегодня: {personal_stats['today']}\n"
        
        stats_text += f"\n🕐 *Обновлено:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        try:
            with open('stats.png', 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=stats_text,
                    parse_mode='Markdown'
                )
            logger.info("Статистика отправлена с картинкой stats.png")
            
        except FileNotFoundError:
            logger.warning("Файл stats.png не найден, отправляем только текст")
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.warning(f"Ошибка отправки фото: {e}, отправляем только текст")
            await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        await update.message.reply_text("❌ Ошибка при получении статистики")

async def my_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Персональная статистика специалиста"""
    try:
        user_id = update.message.from_user.id
        
        if user_id not in SPECIALISTS:
            await update.message.reply_text("❌ Вы не являетесь специалистом системы")
            return
        
        specialist_name = SPECIALISTS[user_id]
        stats = db.get_specialist_stats(specialist_id=user_id)
        
        stats_text = f"👤 *ВАША СТАТИСТИКА* ({specialist_name})\n\n"
        stats_text += f"📊 Всего принято заявок: {stats['total']}\n"
        stats_text += f"✅ Завершено заявок: {stats['completed']}\n"
        stats_text += f"📅 Принято сегодня: {stats['today']}\n"
        
        if stats['total'] > 0:
            completion_rate = (stats['completed'] / stats['total']) * 100
            stats_text += f"📈 Процент завершения: {completion_rate:.1f}%\n"
        
        stats_text += f"\n🕐 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        try:
            with open('stats.png', 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=stats_text,
                    parse_mode='Markdown'
                )
            logger.info("Персональная статистика отправлена с картинкой stats.png")
            
        except FileNotFoundError:
            logger.warning("Файл stats.png не найден, отправляем только текст")
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.warning(f"Ошибка отправки фото: {e}, отправляем только текст")
            await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка при получении персональной статистики: {e}")
        await update.message.reply_text("❌ Ошибка при получении статистики")

async def start_completion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало процесса завершения заявки с комментарием"""
    query = update.callback_query
    await query.answer()
    
    try:
        application_id = int(query.data.split('_')[1])
        specialist_name = SPECIALISTS.get(query.from_user.id, "Специалист")
        
        logger.info(f"START_COMPLETION: Начало завершения заявки #{application_id} специалистом {specialist_name}")
        
        context.user_data.clear()
        context.user_data['completing_application_id'] = application_id
        context.user_data['specialist_name'] = specialist_name
        context.user_data['specialist_id'] = query.from_user.id
        
        logger.info(f"START_COMPLETION: Состояние установлено: {context.user_data}")
        
        comment_text = (
            f"📝 *Завершение заявки #{application_id}*\n\n"
            f"🛠️ *Специалист:* {specialist_name}\n\n"
            "💡 *Опишите решение проблемы подробно:*\n\n"
            "• 🔧 *Что было сделано:* (устранение неисправности, настройка, замена)\n"
            "• ⚙️ *Использованные материалы:* (детали, комплектующие, расходники)\n"
            "• ✅ *Результат:* (проблема решена, требуется проверка, временное решение)\n"
            "• 💬 *Рекомендации пользователю:* (как избежать проблемы в будущем)\n\n"
            "📋 *Этот комментарий будет отправлен пользователю*\n"
            "✍️ *Напишите ваш комментарий в ответ на это сообщение:*"
        )
        
        sent_message = await context.bot.send_message(
            chat_id=CHAT_ID,
            text=comment_text,
            reply_to_message_id=query.message.message_id,
            parse_mode='Markdown'
        )
        
        context.user_data['comment_request_message_id'] = sent_message.message_id
        
        logger.info(f"START_COMPLETION: Запрос комментария отправлен в ГРУППУ для заявки #{application_id}")
        
        return COMMENT
        
    except Exception as e:
        logger.error(f"Ошибка в start_completion: {e}")
        await query.answer("❌ Ошибка при начале завершения заявки", show_alert=True)
        return ConversationHandler.END

async def get_solution_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка комментария решения с картинкой завершения"""
    try:
        logger.info("🎯 GET_SOLUTION_COMMENT: Функция ВЫЗВАНА!")
        
        if update.message.chat_id != CHAT_ID:
            logger.warning(f"GET_SOLUTION_COMMENT: Сообщение пришло не из группового чата: {update.message.chat_id}")
            return ConversationHandler.END
        
        comment = update.message.text
        application_id = context.user_data.get('completing_application_id')
        specialist_name = context.user_data.get('specialist_name')
        
        logger.info(f"📋 GET_SOLUTION_COMMENT: Заявка #{application_id}, Комментарий: '{comment}'")
        logger.info(f"👤 GET_SOLUTION_COMMENT: Специалист: {specialist_name}")
        
        if not application_id:
            logger.error("❌ GET_SOLUTION_COMMENT: application_id не найден в user_data!")
            return ConversationHandler.END
        
        try:
            comment_request_message_id = context.user_data.get('comment_request_message_id')
            if comment_request_message_id:
                await context.bot.delete_message(
                    chat_id=CHAT_ID,
                    message_id=comment_request_message_id
                )
                logger.info(f"GET_SOLUTION_COMMENT: Сообщение с запросом комментария удалено")
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение с запросом комментария: {e}")
        
        logger.info(f"🔄 GET_SOLUTION_COMMENT: Вызов complete_application_with_comment...")
        success, application_data = db.complete_application_with_comment(application_id, comment)
        
        if success and application_data:
            logger.info(f"✅ GET_SOLUTION_COMMENT: Заявка завершена успешно в БД!")
            
            target_user_id = application_data[0]
            user_name = application_data[1]
            user_department = application_data[2]
            audience = application_data[3]
            problem = application_data[4]
            
            logger.info(f"👤 GET_SOLUTION_COMMENT: Пользователь для уведомления: {target_user_id}")
            
            completed_text = (
                f"🏁 *ЗАВЕРШЕНА ЗАЯВКА #{application_id}*\n\n"
                f"👤 *От:* {user_name}\n"
                f"🏢 *Отдел:* {user_department}\n"
                f"📍 *Аудитория:* {audience}\n"
                f"📝 *Проблема:* {problem}\n"
                f"🛠️ *Выполнил:* {specialist_name}\n"
                f"💬 *Решение:* {comment}\n"
                f"✅ *Завершена:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
            
            try:
                message_id = context.bot_data.get(f"application_{application_id}")
                if message_id:
                    await context.bot.edit_message_caption(
                        chat_id=CHAT_ID,
                        message_id=message_id,
                        caption=completed_text,
                        parse_mode='Markdown'
                    )
                    logger.info(f"📢 GET_SOLUTION_COMMENT: Сообщение в группе обновлено")
            except Exception as e:
                logger.warning(f"⚠️ GET_SOLUTION_COMMENT: Не удалось обновить сообщение в группе: {e}")
            
            if target_user_id and target_user_id != 0:
                try:
                    user_notification = (
                        f"🏁 *Ваша заявка #{application_id} завершена!*\n\n"
                        f"📍 *Аудитория:* {audience}\n"
                        f"📋 *Проблема:* {problem}\n"
                        f"🛠️ *Специалист:* {specialist_name}\n\n"
                        f"💡 *Решение:*\n"
                        f"{comment}\n\n"
                        f"✅ *Время завершения:* {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
                        f"⭐ *Сейчас вас попросят оценить работу специалиста*"
                    )
                    
                    try:
                        with open('zvend.png', 'rb') as photo:
                            await context.bot.send_photo(
                                chat_id=target_user_id,
                                photo=photo,
                                caption=user_notification,
                                parse_mode='Markdown'
                            )
                        logger.info(f"📨 GET_SOLUTION_COMMENT: Уведомление о завершении отправлено с картинкой zvend.png пользователю {target_user_id}")
                    except FileNotFoundError:
                        logger.warning("Файл zvend.png не найден, отправляем только текст")
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text=user_notification,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.warning(f"Ошибка отправки фото zvend.png: {e}, отправляем только текст")
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text=user_notification,
                            parse_mode='Markdown'
                        )
                    
                    await request_rating(update, context, application_id, specialist_name)
                    
                except Exception as e:
                    logger.error(f"❌ GET_SOLUTION_COMMENT: Ошибка отправки пользователю {target_user_id}: {e}")
            else:
                logger.warning(f"⚠️ GET_SOLUTION_COMMENT: Неверный user_id для уведомления: {target_user_id}")
            
            await update.message.reply_text(
                f"✅ *Заявка #{application_id} успешно завершена!*\n"
                f"📨 Уведомление отправлено пользователю\n"
                f"⭐ Запрос оценки отправлен",
                parse_mode='Markdown'
            )
            logger.info(f"👨‍💼 GET_SOLUTION_COMMENT: Подтверждение отправлено в группу")
            
        else:
            logger.error(f"❌ GET_SOLUTION_COMMENT: Ошибка завершения заявки в БД")
            await update.message.reply_text(
                "❌ Ошибка при завершении заявки. Возможно, заявка уже обработана.",
                parse_mode='Markdown'
            )
        
        context.user_data.clear()
        logger.info("🧹 GET_SOLUTION_COMMENT: Состояние очищено, возврат ConversationHandler.END")
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"💥 GET_SOLUTION_COMMENT: Критическая ошибка: {e}")
        await update.message.reply_text("❌ Ошибка при обработке комментария")
        context.user_data.clear()
        return ConversationHandler.END

async def request_rating(update: Update, context: ContextTypes.DEFAULT_TYPE, application_id: int, specialist_name: str):
    """Запрос оценки у пользователя после завершения заявки с картинкой"""
    try:
        application_data = db.get_application_by_id(application_id)
        if not application_data:
            logger.error(f"REQUEST_RATING: Заявка #{application_id} не найдена")
            return
        
        user_id = application_data[0]
        user_name = application_data[1] if len(application_data) > 1 else "Пользователь"
        
        logger.info(f"REQUEST_RATING: Отправка запроса оценки пользователю {user_id} для заявки #{application_id}")
        
        rating_text = (
            f"⭐ *ОЦЕНКА СПЕЦИАЛИСТА*\n\n"
            f"📋 *Заявка завершена:* #{application_id}\n"
            f"🛠️ *Специалист:* {specialist_name}\n\n"
            "💡 *Пожалуйста, оцените качество работы:*\n"
            "• 1-3 ⭐ - Плохо (были проблемы)\n"  
            "• 4-7 ⭐ - Нормально (все решено)\n"
            "• 8-10 ⭐ - Отлично (быстро и качественно)\n\n"
            "✨ *Ваша оценка поможет улучшить сервис!*"
        )
        
        keyboard = get_rating_keyboard(application_id)
        logger.info(f"REQUEST_RATING: Создана клавиатура с application_id={application_id}")
        
        try:
            with open('stars1.png', 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=rating_text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            logger.info(f"REQUEST_RATING: Запрос оценки отправлен с картинкой stars1.png пользователю {user_name}")
        except FileNotFoundError:
            logger.warning("Файл stars1.png не найден, отправляем только текст")
            await context.bot.send_message(
                chat_id=user_id,
                text=rating_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.warning(f"Ошибка отправки фото stars1.png: {e}, отправляем только текст")
            await context.bot.send_message(
                chat_id=user_id,
                text=rating_text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
        
    except Exception as e:
        logger.error(f"REQUEST_RATING: Ошибка при запросе оценки: {e}")

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка оценки специалиста"""
    query = update.callback_query
    await query.answer()
    
    try:
        logger.info(f"⭐ HANDLE_RATING: Получен callback_data: {query.data}")
        logger.info(f"⭐ HANDLE_RATING: От пользователя: {query.from_user.id}")
        
        parts = query.data.split('_')
        if len(parts) != 3:
            logger.error(f"⭐ HANDLE_RATING: Неправильный формат callback_data: {query.data}")
            await query.answer("❌ Ошибка формата", show_alert=True)
            return
            
        application_id = int(parts[1])
        rating = int(parts[2])
        
        logger.info(f"⭐ HANDLE_RATING: Оценка {rating} для заявки #{application_id}")
        
        if db.has_application_rating(application_id):
            logger.warning(f"⭐ HANDLE_RATING: Заявка #{application_id} уже имеет оценку")
            await query.answer("❌ Вы уже оценили эту заявку", show_alert=True)
            return
        
        application_data = db.get_application_by_id(application_id)
        if not application_data:
            logger.error(f"⭐ HANDLE_RATING: Заявка #{application_id} не найдена в БД")
            await query.answer("❌ Заявка не найдена", show_alert=True)
            return
        
        specialist_name = application_data[5] if len(application_data) > 5 else "Специалист"
        
        db.save_rating(application_id, None, specialist_name, rating)
        
        thanks_text = (
            f"🙏 *Спасибо за вашу оценку!*\n\n"
            f"📋 *Заявка:* #{application_id}\n"
            f"🛠️ *Специалист:* {specialist_name}\n"
            f"⭐ *Ваша оценка:* {rating}/10\n\n"
            f"💫 *Ваше мнение важно для улучшения сервиса!*"
        )
        
        # Пытаемся отредактировать фото-сообщение
        try:
            await query.edit_message_caption(
                caption=thanks_text,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.warning(f"⭐ HANDLE_RATING: Не удалось редактировать подпись фото: {e}")
            # Если не получилось редактировать фото, пробуем отредактировать текст
            try:
                await query.edit_message_text(
                    text=thanks_text,
                    parse_mode='Markdown'
                )
            except Exception as e2:
                logger.warning(f"⭐ HANDLE_RATING: Не удалось редактировать текст: {e2}")
                # Если и это не получилось, отправляем новое сообщение
                await context.bot.send_message(
                    chat_id=query.from_user.id,
                    text=thanks_text,
                    parse_mode='Markdown'
                )
        
        logger.info(f"⭐ HANDLE_RATING: Оценка {rating} сохранена для заявки #{application_id}")
        
    except Exception as e:
        logger.error(f"❌ HANDLE_RATING: Ошибка при обработке оценки: {e}")
        await query.answer("❌ Ошибка при сохранении оценки", show_alert=True)

async def stars_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для получения статистики оценок"""
    try:
        stats = db.get_all_ratings_stats()
        
        if stats['total_count'] == 0:
            await update.message.reply_text(
                "📊 *Статистика оценок*\n\n"
                "ℹ️ *Пока нет оценок специалистов*\n\n"
                "⭐ *Оценки появляются после завершения заявок,*\n"
                "*когда пользователи оценивают работу специалистов*",
                parse_mode='Markdown'
            )
            return
        
        stars_text = "📊 *СТАТИСТИКА ОЦЕНОК СПЕЦИАЛИСТОВ*\n\n"
        
        stars_text += "📈 *ОБЩАЯ СТАТИСТИКА:*\n"
        stars_text += f"• Всего оценок: {stats['total_count']}\n"
        stars_text += f"• Средний балл: {stats['total_average']}/10\n\n"
        
        if stats['specialists']:
            stars_text += "🏆 *РЕЙТИНГ СПЕЦИАЛИСТОВ:*\n"
            for i, specialist in enumerate(stats['specialists'], 1):
                stars = "⭐" * int(specialist['average'])
                stars_text += f"{i}. {specialist['name']}\n"
                stars_text += f"   ⭐ {specialist['average']}/10 ({specialist['count']} оценок) {stars}\n\n"
        
        stars_text += "📊 *РАСПРЕДЕЛЕНИЕ ОЦЕНОК:*\n"
        for rating in range(1, 11):
            count = stats['distribution'].get(rating, 0)
            percentage = (count / stats['total_count']) * 100 if stats['total_count'] > 0 else 0
            bar = "█" * int(percentage / 5)
            stars_text += f"{rating}⭐: {bar} {count} ({percentage:.1f}%)\n"
        
        stars_text += f"\n🕐 *Обновлено:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        await update.message.reply_text(
            stars_text,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики оценок: {e}")
        await update.message.reply_text(
            "❌ Ошибка при получении статистики оценок",
            parse_mode='Markdown'
        )

async def complete_simple(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Простое завершение заявки без комментария с картинкой"""
    query = update.callback_query
    await query.answer()
    
    try:
        application_id = int(query.data.split('_')[2])
        specialist_name = SPECIALISTS.get(query.from_user.id, "Специалист")
        
        logger.info(f"COMPLETE_SIMPLE: Простое завершение заявки #{application_id} специалистом {specialist_name}")
        
        success, application_data = db.complete_application(application_id)
        
        if success and application_data:
            target_user_id = application_data[0]
            user_name = application_data[1]
            user_department = application_data[2]
            audience = application_data[3]
            problem = application_data[4]
            
            completed_text = (
                f"🏁 *ЗАВЕРШЕНА ЗАЯВКА #{application_id}*\n\n"
                f"👤 *От:* {user_name}\n"
                f"🏢 *Отдел:* {user_department}\n"
                f"📍 *Аудитория:* {audience}\n"
                f"📝 *Проблема:* {problem}\n"
                f"🛠️ *Выполнил:* {specialist_name}\n"
                f"💬 *Решение:* Проблема устранена\n"
                f"✅ *Завершена:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
            
            try:
                message_id = context.bot_data.get(f"application_{application_id}")
                if message_id:
                    await context.bot.edit_message_caption(
                        chat_id=CHAT_ID,
                        message_id=message_id,
                        caption=completed_text,
                        parse_mode='Markdown'
                    )
                    logger.info(f"COMPLETE_SIMPLE: Сообщение в группе обновлено")
            except Exception as e:
                logger.warning(f"COMPLETE_SIMPLE: Не удалось обновить сообщение в группе: {e}")
            
            if target_user_id and target_user_id != 0:
                try:
                    user_notification = (
                        f"🏁 *Ваша заявка #{application_id} завершена!*\n\n"
                        f"📍 *Аудитория:* {audience}\n"
                        f"📋 *Проблема:* {problem}\n"
                        f"🛠️ *Специалист:* {specialist_name}\n\n"
                        f"💡 *Решение:* Проблема устранена\n\n"
                        f"✅ *Время завершения:* {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
                        f"⭐ *Сейчас вас попросят оценить работу специалиста*"
                    )
                    
                    try:
                        with open('zvend.png', 'rb') as photo:
                            await context.bot.send_photo(
                                chat_id=target_user_id,
                                photo=photo,
                                caption=user_notification,
                                parse_mode='Markdown'
                            )
                        logger.info(f"COMPLETE_SIMPLE: Уведомление отправлено с картинкой zvend.png пользователю {target_user_id}")
                    except FileNotFoundError:
                        logger.warning("Файл zvend.png не найден, отправляем только текст")
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text=user_notification,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.warning(f"Ошибка отправки фото zvend.png: {e}, отправляем только текст")
                        await context.bot.send_message(
                            chat_id=target_user_id,
                            text=user_notification,
                            parse_mode='Markdown'
                        )
                    
                    await request_rating(update, context, application_id, specialist_name)
                    
                except Exception as e:
                    logger.error(f"COMPLETE_SIMPLE: Ошибка отправки пользователю {target_user_id}: {e}")
            
            await query.message.reply_text(
                f"✅ *Заявка #{application_id} завершена специалистом {specialist_name}!*\n"
                f"📨 Уведомление отправлено пользователю\n"
                f"⭐ Запрос оценки отправлен",
                parse_mode='Markdown'
            )
            
            logger.info(f"COMPLETE_SIMPLE: Заявка #{application_id} успешно завершена")
            
        else:
            await query.answer("❌ Не удалось завершить заявку", show_alert=True)
            
    except Exception as e:
        logger.error(f"Ошибка в complete_simple: {e}")
        await query.answer("❌ Ошибка при завершении заявки", show_alert=True)

async def stats_zv_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для получения статусов всех заявок"""
    try:
        all_applications = db.get_all_applications()
        
        if not all_applications:
            await update.message.reply_text(
                "📊 *Статистика всех заявок*\n\n"
                "ℹ️ *В системе пока нет заявок*",
                parse_mode='Markdown'
            )
            return
        
        status_groups = {
            'new': [],
            'accepted': [],
            'completed': [],
            'rejected': []
        }
        
        for app in all_applications:
            try:
                app_id = app[0]
                status = app[5] if len(app) > 5 else 'new'
                user_name = app[1] if app[1] else "Неизвестно"
                audience = app[3] if app[3] else "Не указано"
                problem = app[4][:50] + "..." if app[4] and len(app[4]) > 50 else (app[4] if app[4] else "Не указано")
                specialist_name = app[6] if len(app) > 6 and app[6] else "Не назначен"
                
                status_groups[status].append({
                    'id': app_id,
                    'user_name': user_name,
                    'audience': audience,
                    'problem': problem,
                    'specialist': specialist_name
                })
            except Exception as e:
                logger.warning(f"Ошибка обработки заявки {app[0] if app else 'N/A'}: {e}")
                continue
        
        stats_text = "📊 *СТАТУСЫ ВСЕХ ЗАЯВОК*\n\n"
        
        if status_groups['new']:
            stats_text += "🆕 *НОВЫЕ ЗАЯВКИ:*\n"
            for app in status_groups['new']:
                stats_text += f"• #{app['id']} - {app['user_name']} ({app['audience']})\n"
                stats_text += f"  📝 {app['problem']}\n"
                stats_text += f"  👤 Специалист: {app['specialist']}\n\n"
            stats_text += "\n"
        
        if status_groups['accepted']:
            stats_text += "✅ *ЗАЯВКИ В РАБОТЕ:*\n"
            for app in status_groups['accepted']:
                stats_text += f"• #{app['id']} - {app['user_name']} ({app['audience']})\n"
                stats_text += f"  📝 {app['problem']}\n"
                stats_text += f"  👤 Специалист: {app['specialist']}\n\n"
            stats_text += "\n"
        
        if status_groups['completed']:
            stats_text += "🏁 *ЗАВЕРШЕННЫЕ ЗАЯВКИ:*\n"
            for app in status_groups['completed']:
                stats_text += f"• #{app['id']} - {app['user_name']} ({app['audience']})\n"
                stats_text += f"  📝 {app['problem']}\n"
                stats_text += f"  👤 Специалист: {app['specialist']}\n\n"
            stats_text += "\n"
        
        if status_groups['rejected']:
            stats_text += "❌ *ОТКЛОНЕННЫЕ ЗАЯВКИ:*\n"
            for app in status_groups['rejected']:
                stats_text += f"• #{app['id']} - {app['user_name']} ({app['audience']})\n"
                stats_text += f"  📝 {app['problem']}\n"
                stats_text += f"  👤 Специалист: {app['specialist']}\n\n"
        
        total_count = len(all_applications)
        new_count = len(status_groups['new'])
        accepted_count = len(status_groups['accepted'])
        completed_count = len(status_groups['completed'])
        rejected_count = len(status_groups['rejected'])
        
        stats_text += f"📈 *ОБЩАЯ СТАТИСТИКА:*\n"
        stats_text += f"• Всего заявок: {total_count}\n"
        stats_text += f"• 🆕 Новые: {new_count}\n"
        stats_text += f"• ✅ В работе: {accepted_count}\n"
        stats_text += f"• 🏁 Завершены: {completed_count}\n"
        stats_text += f"• ❌ Отклонены: {rejected_count}\n\n"
        
        stats_text += f"🕐 *Обновлено:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        if len(stats_text) > 4000:
            parts = []
            current_part = ""
            lines = stats_text.split('\n')
            
            for line in lines:
                if len(current_part + line + '\n') > 4000:
                    parts.append(current_part)
                    current_part = line + '\n'
                else:
                    current_part += line + '\n'
            
            if current_part:
                parts.append(current_part)
            
            await update.message.reply_text(parts[0], parse_mode='Markdown')
            
            for part in parts[1:]:
                await update.message.reply_text(part, parse_mode='Markdown')
        else:
            await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики всех заявок: {e}")
        await update.message.reply_text(
            "❌ Ошибка при получении статистики заявок",
            parse_mode='Markdown'
        )

async def return_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для показа непринятых заявок со ссылками"""
    try:
        all_applications = db.get_all_applications()
        
        if not all_applications:
            await update.message.reply_text(
                "📋 *Непринятые заявки*\n\n"
                "ℹ️ *В системе пока нет заявок*",
                parse_mode='Markdown'
            )
            return
        
        new_applications = [app for app in all_applications if app[5] == 'new']
        
        if not new_applications:
            await update.message.reply_text(
                "✅ *Непринятые заявки*\n\n"
                "🎉 *Отлично! Все заявки приняты в работу.*\n"
                "Нет непринятых заявок в системе.",
                parse_mode='Markdown'
            )
            return
        
        return_text = "📋 *НЕПРИНЯТЫЕ ЗАЯВКИ*\n\n"
        
        for app in new_applications:
            app_id = app[0]
            user_name = app[1] if app[1] else "Неизвестно"
            user_department = app[2] if app[2] else "Не указано"
            audience = app[3] if app[3] else "Не указано"
            problem = app[4][:100] + "..." if app[4] and len(app[4]) > 100 else (app[4] if app[4] else "Не указано")
            created_date = app[7] if len(app) > 7 and app[7] else "Неизвестно"
            
            try:
                if created_date != "Неизвестно":
                    created_dt = datetime.fromisoformat(created_date)
                    created_str = created_dt.strftime('%d.%m.%Y %H:%M')
                else:
                    created_str = "Неизвестно"
            except:
                created_str = created_date
            
            message_id = db.get_application_message_id(app_id)
            
            return_text += f"🚨 *Заявка #{app_id}*\n"
            return_text += f"👤 *От:* {user_name}\n"
            return_text += f"🏢 *Отдел:* {user_department}\n"
            return_text += f"📍 *Аудитория:* {audience}\n"
            return_text += f"📝 *Проблема:* {problem}\n"
            return_text += f"🕐 *Создана:* {created_str}\n"
            
            if message_id:
                chat_id_str = str(CHAT_ID).replace('-100', '')
                message_link = f"https://t.me/c/{chat_id_str}/{message_id}"
                return_text += f"🔗 [Перейти к заявке]({message_link})\n"
            else:
                return_text += f"🔗 *Ссылка:* Недоступна (сообщение удалено или бот перезапущен)\n"
            
            return_text += "\n" + "─" * 30 + "\n\n"
        
        total_new = len(new_applications)
        total_all = len(all_applications)
        
        return_text += f"📊 *СТАТИСТИКА:*\n"
        return_text += f"• 🆕 Непринятых: {total_new}\n"
        return_text += f"• 📋 Всего заявок: {total_all}\n"
        return_text += f"• ✅ Принятых: {total_all - total_new}\n\n"
        
        return_text += f"💡 *Для принятия заявки перейдите по ссылке и нажмите '✅ Принять'*"
        
        if len(return_text) > 4000:
            parts = []
            current_part = ""
            lines = return_text.split('\n')
            
            for line in lines:
                if len(current_part + line + '\n') > 4000:
                    parts.append(current_part)
                    current_part = line + '\n'
                else:
                    current_part += line + '\n'
            
            if current_part:
                parts.append(current_part)
            
            await update.message.reply_text(parts[0], parse_mode='Markdown', disable_web_page_preview=True)
            
            for part in parts[1:]:
                await update.message.reply_text(part, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            await update.message.reply_text(return_text, parse_mode='Markdown', disable_web_page_preview=True)
        
    except Exception as e:
        logger.error(f"Ошибка при получении непринятых заявок: {e}")
        await update.message.reply_text(
            "❌ Ошибка при получении списка непринятых заявок",
            parse_mode='Markdown'
        )

# Функции для передачи заявок (должны быть в transfer_handlers.py, но добавлены здесь для полноты)
async def start_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начало процесса передачи заявки"""
    query = update.callback_query
    await query.answer()
    
    try:
        application_id = int(query.data.split('_')[1])
        current_specialist_name = SPECIALISTS.get(query.from_user.id, "Специалист")
        
        logger.info(f"START_TRANSFER: Начало передачи заявки #{application_id} от {current_specialist_name}")
        
        transfer_text = (
            f"🔄 *Передача заявки #{application_id}*\n\n"
            f"👤 *Текущий специалист:* {current_specialist_name}\n\n"
            "📋 *Выберите специалиста для передачи:*"
        )
        
        await query.edit_message_caption(
            caption=transfer_text,
            reply_markup=get_specialists_keyboard(application_id),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в start_transfer: {e}")
        await query.answer("❌ Ошибка при передаче заявки", show_alert=True)

async def transfer_to_specialist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Передача заявки выбранному специалисту"""
    query = update.callback_query
    await query.answer()
    
    try:
        parts = query.data.split('_')
        new_specialist_id = int(parts[2])
        application_id = int(parts[3])
        
        current_specialist_id = query.from_user.id
        current_specialist_name = SPECIALISTS.get(current_specialist_id, "Специалист")
        new_specialist_name = SPECIALISTS.get(new_specialist_id, "Специалист")
        
        logger.info(f"TRANSFER_TO_SPECIALIST: Передача заявки #{application_id} от {current_specialist_name} к {new_specialist_name}")
        
        if current_specialist_id == new_specialist_id:
            await query.answer("❌ Нельзя передать заявку самому себе", show_alert=True)
            return
        
        success, application_data, previous_specialist = db.transfer_application(
            application_id, new_specialist_id, new_specialist_name
        )
        
        if success and application_data:
            target_user_id = application_data[0]
            user_name = application_data[1]
            user_department = application_data[2]
            audience = application_data[3]
            problem = application_data[4]
            
            transferred_text = (
                f"🔄 *ПЕРЕДАНА ЗАЯВКА #{application_id}*\n\n"
                f"👤 *От:* {user_name}\n"
                f"🏢 *Отдел:* {user_department}\n"
                f"📍 *Аудитория:* {audience}\n"
                f"📝 *Проблема:* {problem}\n"
                f"🛠️ *Новый специалист:* {new_specialist_name}\n"
                f"⏱️ *Принята:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
            
            try:
                await query.edit_message_caption(
                    caption=transferred_text,
                    reply_markup=get_completion_keyboard(application_id),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.warning(f"Не удалось обновить сообщение в группе: {e}")
            
            try:
                await context.bot.send_message(
                    chat_id=new_specialist_id,
                    text=(
                        f"🔄 *Вам передана заявка #{application_id}*\n\n"
                        f"👤 *От:* {user_name}\n"
                        f"🏢 *Отдел:* {user_department}\n"
                        f"📍 *Аудитория:* {audience}\n"
                        f"📝 *Проблема:* {problem}\n"
                        f"🛠️ *Передал:* {current_specialist_name}\n\n"
                        f"💡 *Заявка ожидает ваших действий в общем чате*"
                    ),
                    parse_mode='Markdown'
                )
                logger.info(f"TRANSFER_TO_SPECIALIST: Уведомление отправлено новому специалисту {new_specialist_name}")
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления новому специалисту: {e}")
            
            if target_user_id:
                try:
                    await context.bot.send_message(
                        chat_id=target_user_id,
                        text=(
                            f"🔄 *Ваша заявка #{application_id} передана другому специалисту*\n\n"
                            f"🛠️ *Новый специалист:* {new_specialist_name}\n"
                            f"💡 *Специалист скоро свяжется с вами*\n\n"
                            f"📍 *Аудитория:* {audience}"
                        ),
                        parse_mode='Markdown'
                    )
                    logger.info(f"TRANSFER_TO_SPECIALIST: Уведомление отправлено пользователю {user_name}")
                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления пользователю: {e}")
            
            try:
                await context.bot.send_message(
                    chat_id=current_specialist_id,
                    text=(
                        f"✅ *Заявка #{application_id} успешно передана*\n\n"
                        f"🛠️ *Новый специалист:* {new_specialist_name}\n"
                        f"👤 *Пользователь:* {user_name}\n"
                        f"📍 *Аудитория:* {audience}"
                    ),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления предыдущему специалисту: {e}")
            
            try:
                await query.message.reply_text(
                    f"🔄 *{current_specialist_name}* передал заявку *#{application_id}* специалисту *{new_specialist_name}*",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.warning(f"Не удалось отправить уведомление в группу: {e}")
                
        else:
            await query.answer("❌ Не удалось передать заявку", show_alert=True)
            
    except Exception as e:
        logger.error(f"Ошибка в transfer_to_specialist: {e}")
        await query.answer("❌ Ошибка при передаче заявки", show_alert=True)

async def cancel_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отмена передачи заявки"""
    query = update.callback_query
    await query.answer("Передача отменена")
    
    try:
        application_id = int(query.data.split('_')[2])
        
        application_data = db.get_application_by_id(application_id)
        if application_data:
            user_name = application_data[1]
            user_department = application_data[2]
            audience = application_data[3]
            problem = application_data[4]
            specialist_name = application_data[5]
            
            application_text = (
                f"✅ *ПРИНЯТА ЗАЯВКА #{application_id}*\n\n"
                f"👤 *От:* {user_name}\n"
                f"🏢 *Отдел:* {user_department}\n"
                f"📍 *Аудитория:* {audience}\n"
                f"📝 *Проблема:* {problem}\n"
                f"🛠️ *Специалист:* {specialist_name}\n"
                f"⏱️ *Принята:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
            
            await query.edit_message_caption(
                caption=application_text,
                reply_markup=get_completion_keyboard(application_id),
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Ошибка в cancel_transfer: {e}")
async def start_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начало процесса передачи заявки"""
    query = update.callback_query
    await query.answer()
    
    try:
        application_id = int(query.data.split('_')[1])
        current_specialist_name = SPECIALISTS.get(query.from_user.id, "Специалист")
        
        logger.info(f"START_TRANSFER: Начало передачи заявки #{application_id} от {current_specialist_name}")
        
        transfer_text = (
            f"🔄 *Передача заявки #{application_id}*\n\n"
            f"👤 *Текущий специалист:* {current_specialist_name}\n\n"
            "📋 *Выберите специалиста для передачи:*"
        )
        
        await query.edit_message_caption(
            caption=transfer_text,
            reply_markup=get_specialists_keyboard(application_id),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в start_transfer: {e}")
        await query.answer("❌ Ошибка при передаче заявки", show_alert=True)

# [file name]: handlers.py
# Замените функцию request_transfer_acceptance на эту версию:

async def request_transfer_acceptance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запрос подтверждения передачи у нового специалиста В ЧАТЕ"""
    query = update.callback_query
    await query.answer()
    
    try:
        parts = query.data.split('_')
        new_specialist_id = int(parts[2])
        application_id = int(parts[3])
        
        current_specialist_id = query.from_user.id
        current_specialist_name = SPECIALISTS.get(current_specialist_id, "Специалист")
        new_specialist_name = SPECIALISTS.get(new_specialist_id, "Специалист")
        
        logger.info(f"REQUEST_TRANSFER: Запрос передачи заявки #{application_id} от {current_specialist_name} к {new_specialist_name}")
        
        if current_specialist_id == new_specialist_id:
            await query.answer("❌ Нельзя передать заявку самому себе", show_alert=True)
            return
        
        # Получаем данные заявки
        application_data = db.get_application_by_id(application_id)
        if application_data:
            user_name = application_data[1]
            user_department = application_data[2]
            audience = application_data[3]
            problem = application_data[4]
            
            # Сохраняем данные о передаче во временное хранилище
            context.bot_data[f'transfer_request_{application_id}'] = {
                'from_specialist_id': current_specialist_id,
                'from_specialist_name': current_specialist_name,
                'to_specialist_id': new_specialist_id,
                'to_specialist_name': new_specialist_name,
                'application_id': application_id,
                'original_message_id': query.message.message_id
            }
            
            # Отправляем запрос В ЧАТЕ с упоминанием специалиста
            transfer_request_text = (
                f"🔄 *ЗАПРОС ПЕРЕДАЧИ ЗАЯВКИ*\n\n"
                f"📋 *Заявка:* #{application_id}\n"
                f"👤 *От пользователя:* {user_name}\n"
                f"🏢 *Отдел:* {user_department}\n"
                f"📍 *Аудитория:* {audience}\n"
                f"📝 *Проблема:* {problem}\n"
                f"🛠️ *Передает:* {current_specialist_name}\n"
                f"👨‍💼 *Назначен:* {new_specialist_name}\n\n"
                f"💡 *{new_specialist_name}, вы хотите принять эту заявку?*"
            )
            
            try:
                # Отправляем запрос в общий чат
                transfer_message = await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=transfer_request_text,
                    reply_markup=get_transfer_acceptance_keyboard(application_id),
                    parse_mode='Markdown'
                )
                
                # Сохраняем ID сообщения с запросом
                context.bot_data[f'transfer_request_{application_id}']['request_message_id'] = transfer_message.message_id
                
                logger.info(f"REQUEST_TRANSFER: Запрос отправлен в чат для специалиста {new_specialist_name}")
                
                # Обновляем оригинальное сообщение в группе
                await query.edit_message_caption(
                    caption=(
                        f"⏳ *ОЖИДАНИЕ ПОДТВЕРЖДЕНИЯ ПЕРЕДАЧИ*\n\n"
                        f"📋 *Заявка:* #{application_id}\n"
                        f"🛠️ *Запрошена передача:* {new_specialist_name}\n"
                        f"⏰ *Ожидание ответа в чате...*"
                    ),
                    parse_mode='Markdown'
                )
                
                await query.answer(f"✅ Запрос передачи отправлен в чат для {new_specialist_name}", show_alert=False)
                
            except Exception as e:
                logger.error(f"Ошибка отправки запроса в чат: {e}")
                await query.answer("❌ Не удалось отправить запрос в чат", show_alert=True)
        else:
            await query.answer("❌ Заявка не найдена", show_alert=True)
            
    except Exception as e:
        logger.error(f"Ошибка в request_transfer_acceptance: {e}")
        await query.answer("❌ Ошибка при запросе передачи", show_alert=True)

# Также обновите функцию handle_transfer_acceptance:

async def handle_transfer_acceptance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка принятия/отклонения/возврата передачи заявки ИЗ ЧАТА"""
    query = update.callback_query
    await query.answer()
    
    try:
        parts = query.data.split('_')
        action = parts[1]  # accept, decline или return
        application_id = int(parts[2])
        
        transfer_data = context.bot_data.get(f'transfer_request_{application_id}')
        if not transfer_data:
            await query.answer("❌ Запрос передачи устарел или не найден", show_alert=True)
            return
        
        from_specialist_id = transfer_data['from_specialist_id']
        from_specialist_name = transfer_data['from_specialist_name']
        to_specialist_id = transfer_data['to_specialist_id']
        to_specialist_name = transfer_data['to_specialist_name']
        original_message_id = transfer_data['original_message_id']
        request_message_id = transfer_data.get('request_message_id')
        
        # Удаляем сообщение с запросом из чата
        if request_message_id:
            try:
                await context.bot.delete_message(
                    chat_id=CHAT_ID,
                    message_id=request_message_id
                )
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение с запросом: {e}")
        
        if action == 'accept':
            # Принятие передачи
            logger.info(f"TRANSFER_ACCEPTED: Специалист {to_specialist_name} принял заявку #{application_id}")
            
            # Обновляем заявку в БД
            success, application_data, previous_specialist = db.transfer_application(
                application_id, to_specialist_id, to_specialist_name
            )
            
            if success and application_data:
                user_id = application_data[0]
                user_name = application_data[1]
                user_department = application_data[2]
                audience = application_data[3]
                problem = application_data[4]
                
                # Обновляем оригинальное сообщение в группе
                transferred_text = (
                    f"✅ *ПЕРЕДАНА ЗАЯВКА #{application_id}*\n\n"
                    f"👤 *От:* {user_name}\n"
                    f"🏢 *Отдел:* {user_department}\n"
                    f"📍 *Аудитория:* {audience}\n"
                    f"📝 *Проблема:* {problem}\n"
                    f"🛠️ *Новый специалист:* {to_specialist_name}\n"
                    f"⏱️ *Принята:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                )
                
                try:
                    await context.bot.edit_message_caption(
                        chat_id=CHAT_ID,
                        message_id=original_message_id,
                        caption=transferred_text,
                        reply_markup=get_completion_keyboard(application_id),
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.warning(f"Не удалось обновить сообщение в группе: {e}")
                
                # Уведомляем в чате о принятии
                try:
                    await context.bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"✅ *{to_specialist_name}* принял передачу заявки *#{application_id}*",
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.warning(f"Не удалось отправить уведомление в чат: {e}")
                
                # Уведомляем предыдущего специалиста
                try:
                    await context.bot.send_message(
                        chat_id=from_specialist_id,
                        text=(
                            f"✅ *Заявка #{application_id} успешно передана*\n\n"
                            f"🛠️ *Новый специалист:* {to_specialist_name}\n"
                            f"👤 *Пользователь:* {user_name}\n"
                            f"📍 *Аудитория:* {audience}"
                        ),
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления предыдущему специалисту: {e}")
                
                # Уведомляем пользователя
                if user_id:
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=(
                                f"🔄 *Ваша заявка #{application_id} передана другому специалисту*\n\n"
                                f"🛠️ *Новый специалист:* {to_specialist_name}\n"
                                f"💡 *Специалист скоро свяжется с вами*\n\n"
                                f"📍 *Аудитория:* {audience}"
                            ),
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Ошибка отправки уведомления пользователю: {e}")
                
            else:
                # Уведомляем в чате об ошибке
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"❌ *Не удалось передать заявку #{application_id}*\n\nЗаявка уже обработана другим специалистом.",
                    parse_mode='Markdown'
                )
        
        elif action == 'decline':
            # Отклонение передачи
            logger.info(f"TRANSFER_DECLINED: Специалист {to_specialist_name} отклонил заявку #{application_id}")
            
            # Восстанавливаем оригинальное сообщение
            try:
                application_data = db.get_application_by_id(application_id)
                if application_data:
                    user_name = application_data[1]
                    user_department = application_data[2]
                    audience = application_data[3]
                    problem = application_data[4]
                    current_specialist_name = application_data[5] if len(application_data) > 5 else from_specialist_name
                    
                    application_text = (
                        f"✅ *ПРИНЯТА ЗАЯВКА #{application_id}*\n\n"
                        f"👤 *От:* {user_name}\n"
                        f"🏢 *Отдел:* {user_department}\n"
                        f"📍 *Аудитория:* {audience}\n"
                        f"📝 *Проблема:* {problem}\n"
                        f"🛠️ *Специалист:* {current_specialist_name}\n"
                        f"⏱️ *Принята:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                    )
                    
                    await context.bot.edit_message_caption(
                        chat_id=CHAT_ID,
                        message_id=original_message_id,
                        caption=application_text,
                        reply_markup=get_completion_keyboard(application_id),
                        parse_mode='Markdown'
                    )
            except Exception as e:
                logger.warning(f"Не удалось восстановить сообщение в группе: {e}")
            
            # Уведомляем в чате об отклонении
            try:
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"❌ *{to_specialist_name}* отклонил передачу заявки *#{application_id}*\n\nЗаявка остается у *{from_specialist_name}*",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.warning(f"Не удалось отправить уведомление в чат: {e}")
        
        elif action == 'return':
            # Возврат заявки предыдущему специалисту
            logger.info(f"TRANSFER_RETURNED: Специалист {to_specialist_name} вернул заявку #{application_id} обратно")
            
            # Восстанавливаем оригинальное сообщение
            try:
                application_data = db.get_application_by_id(application_id)
                if application_data:
                    user_name = application_data[1]
                    user_department = application_data[2]
                    audience = application_data[3]
                    problem = application_data[4]
                    
                    application_text = (
                        f"✅ *ПРИНЯТА ЗАЯВКА #{application_id}*\n\n"
                        f"👤 *От:* {user_name}\n"
                        f"🏢 *Отдел:* {user_department}\n"
                        f"📍 *Аудитория:* {audience}\n"
                        f"📝 *Проблема:* {problem}\n"
                        f"🛠️ *Специалист:* {from_specialist_name}\n"
                        f"⏱️ *Принята:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                    )
                    
                    await context.bot.edit_message_caption(
                        chat_id=CHAT_ID,
                        message_id=original_message_id,
                        caption=application_text,
                        reply_markup=get_completion_keyboard(application_id),
                        parse_mode='Markdown'
                    )
            except Exception as e:
                logger.warning(f"Не удалось восстановить сообщение в группе: {e}")
            
            # Уведомляем в чате о возврате
            try:
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"🔄 *{to_specialist_name}* вернул заявку *#{application_id}* обратно специалисту *{from_specialist_name}*",
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.warning(f"Не удалось отправить уведомление в чат: {e}")
            
            # Уведомляем предыдущего специалиста о возврате
            try:
                application_data = db.get_application_by_id(application_id)
                if application_data:
                    user_name = application_data[1]
                    audience = application_data[3]
                    
                    await context.bot.send_message(
                        chat_id=from_specialist_id,
                        text=(
                            f"🔄 *Заявка возвращена вам*\n\n"
                            f"📋 *Заявка:* #{application_id}\n"
                            f"👤 *Пользователь:* {user_name}\n"
                            f"📍 *Аудитория:* {audience}\n"
                            f"🛠️ *Вернул:* {to_specialist_name}\n\n"
                            f"💡 *Заявка снова назначена на вас*"
                        ),
                        parse_mode='Markdown'
                    )
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления предыдущему специалисту: {e}")
        
        # Очищаем временные данные
        if f'transfer_request_{application_id}' in context.bot_data:
            del context.bot_data[f'transfer_request_{application_id}']
            
    except Exception as e:
        logger.error(f"Ошибка в handle_transfer_acceptance: {e}")
        await query.answer("❌ Ошибка при обработке передачи", show_alert=True)
async def cancel_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отмена передачи заявки на этапе выбора специалиста"""
    query = update.callback_query
    await query.answer("Передача отменена")
    
    try:
        application_id = int(query.data.split('_')[2])
        
        application_data = db.get_application_by_id(application_id)
        if application_data:
            user_name = application_data[1]
            user_department = application_data[2]
            audience = application_data[3]
            problem = application_data[4]
            specialist_name = application_data[5] if len(application_data) > 5 else "Специалист"
            
            application_text = (
                f"✅ *ПРИНЯТА ЗАЯВКА #{application_id}*\n\n"
                f"👤 *От:* {user_name}\n"
                f"🏢 *Отдел:* {user_department}\n"
                f"📍 *Аудитория:* {audience}\n"
                f"📝 *Проблема:* {problem}\n"
                f"🛠️ *Специалист:* {specialist_name}\n"
                f"⏱️ *Принята:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
            
            await query.edit_message_caption(
                caption=application_text,
                reply_markup=get_completion_keyboard(application_id),
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Ошибка в cancel_transfer: {e}")
async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка кнопки обратной связи с картинкой"""
    try:
        feedback_text = (
            "📞 *ОБРАТНАЯ СВЯЗЬ*\n\n"
            "💬 *Для вопросов, предложений и обратной связи:*\n\n"
            "👉 [Перейти в чат обратной связи](https://t.me/+YDotufXOEaBhOTIy)\n\n"
            "📋 *В чате вы можете:*\n"
            "• Задать вопросы по работе системы\n"
            "• Предложить улучшения\n"
            "• Сообщить о проблемах\n"
            "• Получить консультацию\n\n"
            "⚡ *Мы всегда рады вашим отзывам!*"
        )
        
        try:
            with open('obrat.png', 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=feedback_text,
                    reply_markup=get_main_keyboard(),
                    parse_mode='Markdown'
                    # Убрано: disable_web_page_preview=False
                )
            logger.info("Обратная связь отправлена с картинкой obrat.png")
        except FileNotFoundError:
            logger.warning("Файл obrat.png не найден, отправляем только текст")
            await update.message.reply_text(
                feedback_text,
                reply_markup=get_main_keyboard(),
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
        except Exception as e:
            logger.warning(f"Ошибка отправки фото obrat.png: {e}, отправляем только текст")
            await update.message.reply_text(
                feedback_text,
                reply_markup=get_main_keyboard(),
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
        
    except Exception as e:
        logger.error(f"Ошибка в handle_feedback: {e}")
        await update.message.reply_text(
            "❌ Ошибка при обработке запроса",
            reply_markup=get_main_keyboard()
        )

async def faq_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Часто задаваемые вопросы и решения"""
    try:
        faq_text = (
            "❓ *ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ*\n\n"
            
            "🔧 *Проблемы с компьютером:*\n"
            "• *Компьютер не включается:* Проверьте питание, кабели, кнопку включения\n"
            "• *Медленная работа:* Закройте лишние программы, перезагрузите компьютер\n"
            "• *Синий экран:* Запишите код ошибки и сообщите специалисту\n\n"
            
            "🌐 *Проблемы с интернетом:*\n"  
            "• *Нет подключения:* Проверьте кабель Wi-Fi, перезагрузите роутер\n"
            "• *Медленный интернет:* Закройте торренты, видео в HD качестве\n"
            "• *Не открываются сайты:* Попробуйте другой браузер\n\n"
            
            "🖨️ *Проблемы с принтером:*\n"
            "• *Не печатает:* Проверьте бумагу, картриджи, подключение к сети\n"
            "• *Замятие бумаги:* Аккуратно извлеките бумагу по стрелке\n"
            "• *Бледная печать:* Замените картридж\n\n"
            
            "📺 *Проблемы с проектором:*\n"
            "• *Нет изображения:* Проверьте кабель HDMI/VGA, источник сигнала\n"
            "• *Нет звука:* Проверьте громкость, аудиокабель\n"
            "• *Перегрев:* Дайте остыть 30 минут\n\n"
            
            "⚙️ *Программное обеспечение:*\n"
            "• *Не устанавливается:* Проверьте права администратора, место на диске\n"
            "• *Не запускается:* Переустановите программу, проверьте антивирус\n\n"
            
            "💡 *Полезные советы:*\n"
            "• Сохраняйте работу каждые 10-15 минут\n"
            "• Делайте резервные копии важных файлов\n"
            "• Не устанавливайте непроверенное ПО\n"
            "• Регулярно обновляйте систему и программы\n\n"
            
            "📞 *Если проблема не решена:*\n"
            "Создайте заявку через бота с подробным описанием проблемы\n\n"
            "⚡ *Быстрая помощь:* Нажмите *«📝 Оставить заявку»*"
        )
        
        await update.message.reply_text(
            faq_text,
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в faq_command: {e}")
        await update.message.reply_text(
            "❌ Ошибка при загрузке FAQ",
            reply_markup=get_main_keyboard()
        )

async def equipment_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика по проблемам с оборудованием"""
    try:
        user_id = update.message.from_user.id
        
        # Проверяем, является ли пользователь специалистом
        if user_id not in SPECIALISTS:
            await update.message.reply_text(
                "❌ Эта функция доступна только специалистам",
                reply_markup=get_main_keyboard()
            )
            return
        
        # Используем существующие методы из database.py
        all_applications = db.get_all_applications()
        
        if not all_applications:
            await update.message.reply_text(
                "📊 *АНАЛИТИКА ОБОРУДОВАНИЯ*\n\n"
                "ℹ️ В системе пока нет заявок для анализа",
                parse_mode='Markdown'
            )
            return
        
        # Анализируем данные
        audience_stats = {}
        problem_stats = {}
        
        for app in all_applications:
            if len(app) > 3:
                audience = app[3]  # аудитория
                problem = app[4]   # проблема
                
                # Статистика по аудиториям
                if audience:
                    audience_stats[audience] = audience_stats.get(audience, 0) + 1
                
                # Статистика по типам проблем
                problem_lower = problem.lower()
                if any(word in problem_lower for word in ['компьютер', 'пк', 'системник']):
                    problem_stats['💻 Компьютеры'] = problem_stats.get('💻 Компьютеры', 0) + 1
                elif any(word in problem_lower for word in ['интернет', 'сеть', 'wi-fi', 'wifi']):
                    problem_stats['🌐 Интернет'] = problem_stats.get('🌐 Интернет', 0) + 1
                elif any(word in problem_lower for word in ['принтер', 'печать', 'картридж', 'сканер']):
                    problem_stats['🖨️ Принтеры'] = problem_stats.get('🖨️ Принтеры', 0) + 1
                elif any(word in problem_lower for word in ['проектор', 'телевизор', 'тв', 'экран']):
                    problem_stats['📺 Проекторы/ТВ'] = problem_stats.get('📺 Проекторы/ТВ', 0) + 1
                elif any(word in problem_lower for word in ['звук', 'аудио', 'микрофон', 'динамик']):
                    problem_stats['🎤 Аудио'] = problem_stats.get('🎤 Аудио', 0) + 1
                elif any(word in problem_lower for word in ['по', 'программ', 'софт', 'установк']):
                    problem_stats['⚙️ ПО'] = problem_stats.get('⚙️ ПО', 0) + 1
                else:
                    problem_stats['❓ Другое'] = problem_stats.get('❓ Другое', 0) + 1
        
        # Сортируем статистику
        top_audiences = sorted(audience_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        top_problems = sorted(problem_stats.items(), key=lambda x: x[1], reverse=True)
        
        stats_text = "📊 *АНАЛИТИКА ОБОРУДОВАНИЯ*\n\n"
        
        # Топ проблемных аудиторий
        stats_text += "🏢 *ТОП ПРОБЛЕМНЫХ АУДИТОРИЙ:*\n"
        if top_audiences:
            for i, (audience, count) in enumerate(top_audiences, 1):
                stats_text += f"{i}. *{audience}* - {count} заявок\n"
        else:
            stats_text += "Нет данных\n"
        stats_text += "\n"
        
        # Статистика по типам оборудования
        stats_text += "🔧 *СТАТИСТИКА ПО ТИПАМ ПРОБЛЕМ:*\n"
        if top_problems:
            for category, count in top_problems:
                percentage = (count / len(all_applications)) * 100
                stats_text += f"• {category}: {count} ({percentage:.1f}%)\n"
        else:
            stats_text += "Нет данных\n"
        stats_text += "\n"
        
        # Общая статистика
        stats_text += f"📈 *ОБЩАЯ СТАТИСТИКА:*\n"
        stats_text += f"• Всего заявок: {len(all_applications)}\n"
        stats_text += f"• Уникальных аудиторий: {len(audience_stats)}\n"
        stats_text += f"• Категорий проблем: {len(problem_stats)}\n\n"
        
        stats_text += f"🕐 *Обновлено:* {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        await update.message.reply_text(
            stats_text,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в equipment_stats: {e}")
        await update.message.reply_text(
            "❌ Ошибка при получении аналитики",
            parse_mode='Markdown'
        )
async def handle_my_applications_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка кнопки 'Мои заявки'"""
    await my_applications(update, context)

async def handle_faq_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка кнопки 'FAQ' с картинкой"""
    try:
        faq_text = (
            "❓ *ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ*\n\n"
            
            "🔧 *Проблемы с компьютером:*\n"
            "• Не включается: проверьте питание\n"
            "• Медленная работа: перезагрузите\n"
            "• Синий экран: запишите код ошибки\n\n"
            
            "🌐 *Проблемы с интернетом:*\n"  
            "• Нет подключения: перезагрузите роутер\n"
            "• Медленный интернет: закройте торренты\n"
            "• Не открываются сайты: смените браузер\n\n"
            
            "🖨️ *Проблемы с принтером:*\n"
            "• Не печатает: проверьте бумагу и картриджи\n"
            "• Замятие бумаги: аккуратно извлеките\n"
            "• Бледная печать: замените картридж\n\n"
            
            "📺 *Проблемы с проектором:*\n"
            "• Нет изображения: проверьте кабель\n"
            "• Нет звука: проверьте громкость\n"
            "• Перегрев: дайте остыть 30 минут\n\n"
            
            "⚡ *Быстрая помощь:* Нажмите *«📝 Оставить заявку»*"
        )
        
        try:
            with open('faq.png', 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=faq_text,
                    reply_markup=get_main_keyboard(),
                    parse_mode='Markdown'
                )
            logger.info("FAQ отправлен с картинкой faq.png")
        except FileNotFoundError:
            logger.warning("Файл faq.png не найден, отправляем только текст")
            await update.message.reply_text(
                faq_text,
                reply_markup=get_main_keyboard(),
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.warning(f"Ошибка отправки фото faq.png: {e}, отправляем только текст")
            await update.message.reply_text(
                faq_text,
                reply_markup=get_main_keyboard(),
                parse_mode='Markdown'
            )
        
    except Exception as e:
        logger.error(f"Ошибка в handle_faq_button: {e}")
        await update.message.reply_text(
            "❌ Ошибка при загрузке FAQ",
            reply_markup=get_main_keyboard()
        )
async def my_applications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все заявки пользователя с их статусами"""
    try:
        user_id = update.message.from_user.id
        
        # Используем метод из database.py через существующее соединение
        conn = sqlite3.connect('applications.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, audience, problem, status, created_date, specialist_name, completed_date 
            FROM applications 
            WHERE user_id = ? 
            ORDER BY id DESC
        ''', (user_id,))
        applications = cursor.fetchall()
        conn.close()
        
        if not applications:
            await update.message.reply_text(
                "📋 *ВАШИ ЗАЯВКИ*\n\n"
                "У вас пока нет созданных заявок.\n\n"
                "💡 Хотите создать первую заявку? Нажмите *«📝 Оставить заявку»*",
                reply_markup=get_main_keyboard(),
                parse_mode='Markdown'
            )
            return
        
        applications_text = "📋 *ВАШИ ЗАЯВКИ*\n\n"
        
        for app in applications:
            app_id, audience, problem, status, created_date, specialist_name, completed_date = app
            
            # Эмодзи статусов
            status_emojis = {
                'new': '🆕',
                'accepted': '🛠️',
                'completed': '✅',
                'rejected': '❌'
            }
            
            emoji = status_emojis.get(status, '📝')
            status_texts = {
                'new': 'Ожидает специалиста',
                'accepted': 'В работе',
                'completed': 'Завершена', 
                'rejected': 'Отклонена'
            }
            
            status_text = status_texts.get(status, status)
            
            applications_text += f"{emoji} *Заявка #{app_id}*\n"
            applications_text += f"📍 *Аудитория:* {audience}\n"
            applications_text += f"📝 *Проблема:* {problem[:80]}{'...' if len(problem) > 80 else ''}\n"
            applications_text += f"📊 *Статус:* {status_text}\n"
            
            if specialist_name:
                applications_text += f"👨‍💼 *Специалист:* {specialist_name}\n"
            
            # Форматируем дату
            try:
                created_dt = datetime.fromisoformat(created_date)
                created_str = created_dt.strftime('%d.%m.%Y %H:%M')
                applications_text += f"🕐 *Создана:* {created_str}\n"
            except:
                applications_text += f"🕐 *Создана:* {created_date}\n"
            
            if completed_date and status == 'completed':
                try:
                    completed_dt = datetime.fromisoformat(completed_date)
                    completed_str = completed_dt.strftime('%d.%m.%Y %H:%M')
                    applications_text += f"✅ *Завершена:* {completed_str}\n"
                except:
                    applications_text += f"✅ *Завершена:* {completed_date}\n"
            
            applications_text += "─" * 30 + "\n\n"
        
        # Статистика
        total = len(applications)
        new_count = len([a for a in applications if a[3] == 'new'])
        accepted_count = len([a for a in applications if a[3] == 'accepted'])
        completed_count = len([a for a in applications if a[3] == 'completed'])
        
        applications_text += f"📊 *СТАТИСТИКА:*\n"
        applications_text += f"• Всего заявок: {total}\n"
        applications_text += f"• 🆕 Ожидают: {new_count}\n"
        applications_text += f"• 🛠️ В работе: {accepted_count}\n"
        applications_text += f"• ✅ Завершено: {completed_count}\n\n"
        
        applications_text += "💡 *Для создания новой заявки нажмите «📝 Оставить заявку»*"
        
        await update.message.reply_text(
            applications_text,
            reply_markup=get_main_keyboard(),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в my_applications: {e}")
        await update.message.reply_text(
            "❌ Ошибка при получении списка заявок",
            reply_markup=get_main_keyboard()
        )

async def handle_my_applications_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка кнопки 'Мои заявки'"""
    await my_applications(update, context)
async def get_help_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка выбора типа помощи"""
    try:
        user_id = update.message.from_user.id
        user_message = update.message.text
        
        # Обрабатываем выбор типа помощи
        if user_message in ["💻 Дистанционная помощь", "🔧 Помощь в очной форме"]:
            context.user_data['help_type'] = user_message
            
            # Удаляем предыдущее сообщение бота
            try:
                if user_id in bot_messages_to_delete:
                    for msg_id in bot_messages_to_delete[user_id]:
                        try:
                            await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                        except Exception as e:
                            logger.warning(f"Не удалось удалить сообщение бота: {e}")
                    bot_messages_to_delete[user_id] = []
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение: {e}")
            
            # Запрашиваем проблему с картинкой
            problem_text = (
                "🔧 *Выберите тип проблемы*\n\n"
                "💡 *Вы можете выбрать один из вариантов ниже:*\n\n"
                "• 💻 *Компьютер* - не включается, иные проблемы\n"
                "• 🌐 *Интернет* - нет подключения, долгая загрузка\n"
                "• 🖨️ *Принтер* - замена картриджа, настройка, замятие, сканер\n"
                "• 📺 *Проектор/Телевизор* - нет изображения, звука\n"
                "• ⚙️ *Программное обеспечение* - установка, настройка программ\n"
                "• 🎤 *Аудио* - запись мероприятий, настройка оборудования\n"
                "• ❓ *Другое* - опишите проблему в свободной форме\n\n"
                "📝 *Выберите вариант ниже 👇*"
            )
            
            try:
                with open('typepr.png', 'rb') as photo:
                    sent_message = await update.message.reply_photo(
                        photo=photo,
                        caption=problem_text,
                        reply_markup=get_problem_keyboard(),
                        parse_mode='Markdown'
                    )
                logger.info("Выбор типа проблемы отправлен с картинкой typepr.png")
            except FileNotFoundError:
                logger.warning("Файл typepr.png не найден, отправляем только текст")
                sent_message = await update.message.reply_text(
                    problem_text,
                    reply_markup=get_problem_keyboard(),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.warning(f"Ошибка отправки фото typepr.png: {e}, отправляем только текст")
                sent_message = await update.message.reply_text(
                    problem_text,
                    reply_markup=get_problem_keyboard(),
                    parse_mode='Markdown'
                )
            
            bot_messages_to_delete[user_id].append(sent_message.message_id)
            return PROBLEM
        
        # Обрабатываем кнопку "Назад"
        elif user_message == "🔙 Назад":
            # Удаляем предыдущее сообщение бота
            try:
                if user_id in bot_messages_to_delete:
                    for msg_id in bot_messages_to_delete[user_id]:
                        try:
                            await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                        except Exception as e:
                            logger.warning(f"Не удалось удалить сообщение бота: {e}")
                    bot_messages_to_delete[user_id] = []
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение: {e}")
            
            # Возвращаем к вводу аудитории
            sent_message = await update.message.reply_text(
                "В какой аудитории найдена проблема?",
                reply_markup=remove_keyboard()
            )
            
            bot_messages_to_delete[user_id].append(sent_message.message_id)
            return AUDIENCE
        
        else:
            # Если получен неожиданный ввод, просим выбрать из предложенных вариантов
            await update.message.reply_text(
                "Пожалуйста, выберите тип помощи из предложенных вариантов:",
                reply_markup=get_help_type_keyboard()
            )
            return HELP_TYPE
        
    except Exception as e:
        logger.error(f"Ошибка в get_help_type: {e}")
        return ConversationHandler.END
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда помощи с описанием всех команд (только для специалистов в чате)"""
    try:
        user_id = update.message.from_user.id
        chat_id = update.message.chat_id
        
        # Проверяем, что команда вызвана в групповом чате и пользователь - специалист
        if chat_id != CHAT_ID:
            await update.message.reply_text(
                "❌ Эта команда доступна только в групповом чате специалистов",
                parse_mode='Markdown'
            )
            return
            
        if user_id not in SPECIALISTS:
            await update.message.reply_text(
                "❌ Эта команда доступна только специалистам",
                parse_mode='Markdown'
            )
            return
        
        help_text = (
            "🛠️ *КОМАНДЫ ДЛЯ СПЕЦИАЛИСТОВ*\n\n"
            
            "📋 *Основные команды:*\n"
            "• `/stats` - общая статистика заявок\n"
            "• `/statszv` - статусы всех заявок\n"
            "• `/return` - непринятые заявки со ссылками\n"
            "• `/stars` - статистика оценок\n"
            "• `/mystats` - ваша персональная статистика\n"
            "• `/equipment` - аналитика оборудования\n"
            "• `/my_id` - узнать ваш ID\n\n"
            
            "🔄 *Действия с заявками:*\n"
            "• *✅ Принять* - взять заявку в работу\n"
            "• *❌ Отклонить* - отклонить заявку\n"
            "• *💬 Завершить с комментарием* - завершить с описанием решения\n"
            "• *✅ Завершить* - завершить без комментария\n"
            "• *🔄 Передать другому* - передать заявку коллеге\n\n"
            
            "📊 *Процесс работы:*\n"
            "1. *Новая заявка* → Принять/Отклонить\n"
            "2. *Принятая заявка* → Завершить/Передать\n"
            "3. *Завершенная заявка* → Пользователь оценивает работу\n\n"
            
            "💡 *Советы:*\n"
            "• Используйте комментарии для подробного описания решения\n"
            "• Передавайте заявки если не можете оперативно решить проблему\n"
            "• Отслеживайте статистику для анализа эффективности\n\n"
            
            "⚡ *Быстрые действия всегда доступны под сообщениями с заявками!*"
        )
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в help_command: {e}")
# [file name]: handlers.py
# Замените функцию obossan_command на эту версию:

async def obossan_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для похвалы специалиста (50/50 между двумя фразами)"""
    try:
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id
        
        # Проверяем, что команда вызвана в ответ на сообщение специалиста
        if not update.message.reply_to_message:
            await update.message.reply_text(
                "❌ *Как использовать команду:*\n\n"
                "Ответьте на сообщение специалиста и напишите `/obossan`",
                parse_mode='Markdown'
            )
            return
        
        # Получаем ID специалиста из сообщения, на которое ответили
        specialist_id = update.message.reply_to_message.from_user.id
        
        # Проверяем, что это действительно специалист
        if specialist_id not in SPECIALISTS:
            await update.message.reply_text(
                "❌ *Этот пользователь не является специалистом*\n\n"
                "Команда работает только с зарегистрированными специалистами",
                parse_mode='Markdown'
            )
            return
        
        specialist_name = SPECIALISTS[specialist_id]
        
        # 50/50 между двумя фразами
        import random
        if random.choice([True, False]):
            compliment = f"*{specialist_name}* - Не был сегодня обоссан! Поздравим его!"
        else:
            compliment = f"*{specialist_name}* - Был обоссан! Ахахахах("
        
        # Отправляем похвалу
        await update.message.reply_text(
            compliment,
            parse_mode='Markdown'
        )
        
        # Удаляем исходную команду чтобы не засорять чат
        try:
            await update.message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение с командой: {e}")
        
        logger.info(f"OBOSSAN: Пользователь {user_id} похвалил специалиста {specialist_name} (фраза: {'огонь' if 'огонь' in compliment else 'звезда'})")
        
    except Exception as e:
        logger.error(f"Ошибка в obossan_command: {e}")
        await update.message.reply_text(
            "❌ Ошибка при выполнении команды",
            parse_mode='Markdown'
        )