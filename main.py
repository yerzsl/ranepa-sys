import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from telegram import BotCommand, BotCommandScopeAllPrivateChats, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN, FIO, DEPARTMENT, AUDIENCE, PROBLEM, COMMENT, HELP_TYPE
from handlers import (
    start, get_fio, get_department, start_application, 
    get_audience, get_problem, cancel, handle_message, 
    get_chat_id, handle_application_action, stats_command, my_stats,
    start_completion, get_solution_comment, stats_zv_command, return_command,
    stars_command, handle_rating, complete_simple, handle_feedback,
    start_transfer, request_transfer_acceptance, handle_transfer_acceptance, cancel_transfer,
    my_applications, faq_command, equipment_stats,
    handle_my_applications_button, handle_faq_button, handle_menu_button, get_help_type,
    help_command, obossan_command
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def webapp_command(update, context):
    """Команда для открытия Mini App"""
    keyboard = [
        [InlineKeyboardButton(
            "📱 Открыть приложение", 
            web_app=WebAppInfo(url="https://your-domain.com/webapp/")
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🚀 *Откройте веб-приложение для удобной работы с системой:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def setup_commands(application):
    """Настройка команд бота"""
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("app", "Открыть веб-приложение"),
        BotCommand("myapps", "Мои заявки"),
        BotCommand("stats", "Статистика"),
        BotCommand("help", "Помощь")
    ]
    await application.bot.set_my_commands(commands, scope=BotCommandScopeAllPrivateChats())

def main():
    """Основная функция запуска бота"""
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Обработчик завершения с комментарием
        completion_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(start_completion, pattern="^complete_\\d+$")],
            states={
                COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_solution_comment)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_message=False
        )
        
        # Регистрация обработчиков
        application.add_handler(completion_handler)
        
        # Регистрация пользователя
        application.add_handler(ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, get_fio)],
                DEPARTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, get_department)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        ))
        
        # Создание заявки
        application.add_handler(ConversationHandler(
            entry_points=[MessageHandler(filters.Regex('^📝 Оставить заявку$') & filters.ChatType.PRIVATE, start_application)],
            states={
                AUDIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, get_audience)],
                HELP_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, get_help_type)],
                PROBLEM: [MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, get_problem)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        ))
        
        # ОБРАБОТЧИКИ CALLBACK
        application.add_handler(CallbackQueryHandler(handle_rating, pattern="^rate_"))
        application.add_handler(CallbackQueryHandler(complete_simple, pattern="^complete_simple_"))
        application.add_handler(CallbackQueryHandler(handle_application_action, pattern="^(accept|reject)_"))
        application.add_handler(CallbackQueryHandler(start_transfer, pattern="^transfer_\\d+$"))
        application.add_handler(CallbackQueryHandler(request_transfer_acceptance, pattern="^transfer_to_"))
        application.add_handler(CallbackQueryHandler(handle_transfer_acceptance, pattern="^transfer_(accept|decline|return)_"))
        application.add_handler(CallbackQueryHandler(cancel_transfer, pattern="^cancel_transfer_"))
        
        # КОМАНДЫ
        application.add_handler(CommandHandler("app", webapp_command))
        application.add_handler(CommandHandler("myapps", my_applications, filters.ChatType.PRIVATE))
        application.add_handler(CommandHandler("faq", faq_command, filters.ChatType.PRIVATE))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("statszv", stats_zv_command))
        application.add_handler(CommandHandler("return", return_command))
        application.add_handler(CommandHandler("stars", stars_command))
        application.add_handler(CommandHandler("mystats", my_stats))
        application.add_handler(CommandHandler("equipment", equipment_stats))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("my_id", get_chat_id))
        application.add_handler(CommandHandler("obossan", obossan_command))
        
        # ОБРАБОТЧИКИ КНОПОК
        application.add_handler(MessageHandler(filters.Regex('^📝 Оставить заявку$') & filters.ChatType.PRIVATE, start_application))
        application.add_handler(MessageHandler(filters.Regex('^📋 Мои заявки$') & filters.ChatType.PRIVATE, handle_my_applications_button))
        application.add_handler(MessageHandler(filters.Regex('^❓ FAQ$') & filters.ChatType.PRIVATE, handle_faq_button))
        application.add_handler(MessageHandler(filters.Regex('^📞 Обратная связь$') & filters.ChatType.PRIVATE, handle_feedback))
        application.add_handler(MessageHandler(filters.Regex('^🏠 Меню$') & filters.ChatType.PRIVATE, handle_menu_button))
        
        # ОБЫЧНЫЕ ОБРАБОТЧИКИ
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_message))
        
        # Настройка команд при запуске
        application.post_init = setup_commands
        
        logger.info("Бот запущен")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")

if __name__ == '__main__':
    main()