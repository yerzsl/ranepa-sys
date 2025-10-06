import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'https://your-app.railway.app')

async def start(update, context):
    """Команда /start"""
    keyboard = [
        [InlineKeyboardButton("📱 Открыть приложение", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("📝 Оставить заявку", callback_data="create_app")]
    ]
    
    await update.message.reply_text(
        "🚀 Добро пожаловать в RANEPA.SYSTEM!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def webapp_command(update, context):
    """Команда /app"""
    keyboard = [[InlineKeyboardButton("📱 Открыть приложение", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(
        "Откройте веб-приложение:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("app", webapp_command))
    
    logger.info("Бот запущен")
    application.run_polling()

if __name__ == '__main__':
    main()