from telebot import types
from firebase_db import FirebaseDB
from firebase_db import db
from config import Config
from datetime import datetime
from utils.keyboard_utils import create_category_keyboard, create_back_button


def register_admin_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == '👨‍💼 Админ панель')
    def handle_admin_panel(message):
        user_id = message.from_user.id
        user = FirebaseDB.get_user(user_id)

        if not user or user['role'] != 'admin':
            bot.send_message(message.chat.id, "У вас нет доступа к админ панели")
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('📊 Статистика пользователей')
        btn2 = types.KeyboardButton('➕ Добавить товар')
        btn3 = types.KeyboardButton('📝 Создать тест')
        markup.add(btn1, btn2, btn3)
        markup.add(types.KeyboardButton('🔙 Назад'))

        bot.send_message(
            message.chat.id,
            "👨‍💼 <b>Административная панель</b>\n\n"
            "Выберите действие:",
            parse_mode='HTML',
            reply_markup=markup
        )

    @bot.message_handler(func=lambda message: message.text == '📊 Статистика пользователей')
    def handle_user_stats(message):
        users_ref = db.collection('users')
        users = [doc.to_dict() for doc in users_ref.stream()]

        stats_text = "📊 <b>Статистика пользователей</b>\n\n"
        stats_text += f"👥 Всего пользователей: {len(users)}\n"
        stats_text += f"👑 Администраторов: {sum(1 for u in users if u.get('role') == 'admin')}\n"

        bot.send_message(
            message.chat.id,
            stats_text,
            parse_mode='HTML',
            reply_markup=create_back_button()
        )

    @bot.message_handler(func=lambda message: message.text == '➕ Добавить товар')
    def handle_add_product(message):
        bot.send_message(
            message.chat.id,
            "Введите название нового товара:",
            parse_mode='HTML',
            reply_markup=create_back_button()
        )
        bot.register_next_step_handler(message, process_product_name)

    def process_product_name(message):
        if message.text == '🔙 Назад':
            handle_admin_panel(message)
            return

        product_name = message.text.strip()
        if not product_name:
            bot.send_message(message.chat.id, "Название товара не может быть пустым")
            return

        categories = FirebaseDB.get_categories()
        if not categories:
            categories = [{'name': cat, 'id': idx} for idx, cat in enumerate(Config.PRODUCT_CATEGORIES)]

        bot.send_message(
            message.chat.id,
            "Выберите категорию для товара:",
            reply_markup=create_category_keyboard(categories)
        )
        bot.register_next_step_handler(message, process_product_category, product_name)

    def process_product_category(message, product_name):
        if message.text == '🔙 Назад':
            handle_add_product(message)
            return

        category_name = message.text.replace('Категория: ', '')
        categories = FirebaseDB.get_categories()
        category = next((cat for cat in categories if cat['name'] == category_name), None)

        if not category:
            bot.send_message(message.chat.id, "Категория не найдена")
            return

        bot.send_message(
            message.chat.id,
            "Введите описание товара:",
            parse_mode='HTML',
            reply_markup=create_back_button()
        )
        bot.register_next_step_handler(message, process_product_description, product_name, category['id'])

    def process_product_description(message, product_name, category_id):
        if message.text == '🔙 Назад':
            handle_add_product(message)
            return

        description = message.text.strip()

        product_data = {
            'name': product_name,
            'category_id': category_id,
            'description': description,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

        FirebaseDB.create_product(product_data)
        bot.send_message(
            message.chat.id,
            f"Товар '{product_name}' успешно добавлен!",
            parse_mode='HTML'
        )
        handle_admin_panel(message)

    @bot.message_handler(func=lambda message: message.text == '📝 Создать тест')
    def handle_create_test(message):
        bot.send_message(
            message.chat.id,
            "Введите название нового теста:",
            parse_mode='HTML',
            reply_markup=create_back_button()
        )
        bot.register_next_step_handler(message, process_test_title)

    def process_test_title(message):
        if message.text == '🔙 Назад':
            handle_admin_panel(message)
            return

        test_title = message.text.strip()
        if not test_title:
            bot.send_message(message.chat.id, "Название теста не может быть пустым")
            return

        bot.send_message(
            message.chat.id,
            "Введите описание теста:",
            parse_mode='HTML',
            reply_markup=create_back_button()
        )
        bot.register_next_step_handler(message, process_test_description, test_title)

    def process_test_description(message, test_title):
        if message.text == '🔙 Назад':
            handle_create_test(message)
            return

        description = message.text.strip()

        bot.send_message(
            message.chat.id,
            "Введите проходной балл (минимальное количество правильных ответов для успешного прохождения):",
            parse_mode='HTML',
            reply_markup=create_back_button()
        )
        bot.register_next_step_handler(message, process_passing_score, test_title, description)

    def process_passing_score(message, test_title, description):
        if message.text == '🔙 Назад':
            handle_create_test(message)
            return

        try:
            passing_score = int(message.text.strip())
            if passing_score <= 0:
                raise ValueError
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите положительное целое число")
            return

        test_data = {
            'title': test_title,
            'description': description,
            'passing_score': passing_score,
            'questions': [],
            'created_at': FirebaseDB.datetime.now()
        }

        bot.send_message(
            message.chat.id,
            "Теперь будем добавлять вопросы. Введите текст первого вопроса:",
            parse_mode='HTML',
            reply_markup=create_back_button()
        )
        bot.register_next_step_handler(message, process_question_text, test_data)

    def process_question_text(message, test_data):
        if message.text == '🔙 Назад':
            handle_create_test(message)
            return

        question_text = message.text.strip()
        if not question_text:
            bot.send_message(message.chat.id, "Текст вопроса не может быть пустым")
            return

        question = {
            'text': question_text,
            'options': [],
            'correct_answer': ''
        }

        bot.send_message(
            message.chat.id,
            "Введите вариант ответа (первый вариант будет считаться правильным, затем можно добавить другие варианты):",
            parse_mode='HTML',
            reply_markup=types.ForceReply(selective=False)
        )
        bot.register_next_step_handler(message, process_answer_option, test_data, question, 0)

    def process_answer_option(message, test_data, question, option_index):
        if message.text == '🔙 Назад':
            handle_create_test(message)
            return

        option_text = message.text.strip()
        if not option_text:
            bot.send_message(message.chat.id, "Вариант ответа не может быть пустым")
            return

        if option_index == 0:
            question['correct_answer'] = option_text

        question['options'].append(option_text)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_add = types.KeyboardButton('➕ Добавить вариант')
        btn_done = types.KeyboardButton('✅ Завершить вопрос')
        markup.add(btn_add, btn_done)
        markup.add(types.KeyboardButton('🔙 Назад'))

        bot.send_message(
            message.chat.id,
            f"Добавлен вариант: {option_text}\n\n"
            f"Текущие варианты:\n" + "\n".join(f"{i + 1}. {opt}" for i, opt in enumerate(question['options'])) + "\n\n"
                                                                                                                 "Добавить еще вариант или завершить вопрос?",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, process_add_more_options, test_data, question)

    def process_add_more_options(message, test_data, question):
        if message.text == '🔙 Назад':
            handle_create_test(message)
            return
        elif message.text == '➕ Добавить вариант':
            bot.send_message(
                message.chat.id,
                "Введите следующий вариант ответа:",
                parse_mode='HTML',
                reply_markup=types.ForceReply(selective=False)
            )
            bot.register_next_step_handler(message, process_answer_option, test_data, question,
                                           len(question['options']))
        elif message.text == '✅ Завершить вопрос':
            test_data['questions'].append(question)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn_add = types.KeyboardButton('➕ Добавить вопрос')
            btn_done = types.KeyboardButton('✅ Завершить тест')
            markup.add(btn_add, btn_done)
            markup.add(types.KeyboardButton('🔙 Назад'))

            bot.send_message(
                message.chat.id,
                f"Вопрос добавлен. Всего вопросов: {len(test_data['questions'])}\n\n"
                "Добавить еще вопрос или завершить создание теста?",
                reply_markup=markup
            )
            bot.register_next_step_handler(message, process_add_more_questions, test_data)

    def process_add_more_questions(message, test_data):
        if message.text == '🔙 Назад':
            handle_create_test(message)
            return
        elif message.text == '➕ Добавить вопрос':
            bot.send_message(
                message.chat.id,
                "Введите текст следующего вопроса:",
                parse_mode='HTML',
                reply_markup=create_back_button()
            )
            bot.register_next_step_handler(message, process_question_text, test_data)
        elif message.text == '✅ Завершить тест':
            if len(test_data['questions']) < 1:
                bot.send_message(message.chat.id, "Тест должен содержать хотя бы один вопрос")
                return

            test = FirebaseDB.create_test(test_data)
            bot.send_message(
                message.chat.id,
                f"✅ Тест '{test['title']}' успешно создан!\n"
                f"Количество вопросов: {len(test['questions'])}\n"
                f"Проходной балл: {test['passing_score']}",
                parse_mode='HTML'
            )
            handle_admin_panel(message)