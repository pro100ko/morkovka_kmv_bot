import telebot
from telebot import types
from datetime import datetime
from config import Config
from firebase_db import FirebaseDB
from handlers.user_management import register_user_handlers
from handlers.knowledge_base import register_knowledge_base_handlers
from handlers.testing import register_testing_handlers
from handlers.admin import register_admin_handlers
from handlers.common import register_common_handlers

bot = telebot.TeleBot(Config.BOT_TOKEN)

# Регистрация обработчиков
register_common_handlers(bot)
register_user_handlers(bot)
register_knowledge_base_handlers(bot)
register_testing_handlers(bot)
register_admin_handlers(bot)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user = FirebaseDB.get_user(user_id)

    if not user:
        user_data = {
            'user_id': user_id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'role': 'admin' if user_id in Config.ADMIN_IDS else 'user',
            'registration_date': datetime.now(),
            'last_activity': datetime.now()
        }
        FirebaseDB.create_user(user_data)
        user = user_data

    FirebaseDB.update_user(user_id, {'last_activity': datetime.now()})

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('📚 База знаний')
    btn2 = types.KeyboardButton('📝 Тестирование')
    markup.add(btn1, btn2)

    if user['role'] == 'admin':
        btn3 = types.KeyboardButton('👨‍💼 Админ панель')
        markup.add(btn3)

    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! Я бот 'Морковка КМВ' - твой помощник в изучении ассортимента.",
        reply_markup=markup
    )


if __name__ == '__main__':
    print("Бот запущен!")
    bot.polling(none_stop=True)