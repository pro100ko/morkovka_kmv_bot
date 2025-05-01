from telebot import types
from firebase_db import FirebaseDB
from utils.keyboard_utils import create_back_button


def register_common_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == '🔙 Назад')
    def handle_back(message):
        user = FirebaseDB.get_user(message.from_user.id)
        if not user:
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('📚 База знаний')
        btn2 = types.KeyboardButton('📝 Тестирование')
        markup.add(btn1, btn2)

        if user['role'] == 'admin':
            btn3 = types.KeyboardButton('👨‍💼 Админ панель')
            markup.add(btn3)

        bot.send_message(
            message.chat.id,
            "Вы вернулись в главное меню",
            reply_markup=markup
        )