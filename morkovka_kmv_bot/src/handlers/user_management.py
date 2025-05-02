from telebot import types
from firebase_db import FirebaseDB
from utils.keyboard_utils import create_back_button


def register_user_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == '👤 Мой профиль')
    def handle_profile(message):
        user_id = message.from_user.id
        user = FirebaseDB.get_user(user_id)
        if not user:
            return

        test_results = FirebaseDB.get_user_test_results(user_id)
        passed_tests = sum(1 for result in test_results if result['passed'])
        total_tests = len(test_results)

        profile_text = (
            f"👤 <b>Ваш профиль</b>\n\n"
            f"🆔 ID: {user_id}\n"
            f"👤 Имя: {user.get('first_name', '')} {user.get('last_name', '')}\n"
            f"📅 Дата регистрации: {user.get('registration_date', 'Неизвестно')}\n\n"
            f"📊 <b>Статистика тестов</b>\n"
            f"✅ Пройдено тестов: {passed_tests}\n"
            f"📝 Всего тестов: {total_tests}"
        )

        bot.send_message(
            message.chat.id,
            profile_text,
            parse_mode='HTML',
            reply_markup=create_back_button()
        )