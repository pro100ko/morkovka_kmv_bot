from telebot import types
from firebase_admin import firestore
from datetime import datetime
from firebase_db import FirebaseDB
from config import Config
from utils.keyboard_utils import create_back_button
import random


def register_testing_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == '📝 Тестирование')
    def handle_testing(message):
        tests = FirebaseDB.get_tests()
        if not tests:
            bot.send_message(message.chat.id, "На данный момент нет доступных тестов")
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for test in tests:
            markup.add(types.KeyboardButton(f"Тест: {test['title']}"))

        markup.add(types.KeyboardButton('🔙 Назад'))

        bot.send_message(
            message.chat.id,
            "📝 <b>Доступные тесты</b>\n\n"
            "Выберите тест для прохождения:",
            parse_mode='HTML',
            reply_markup=markup
        )

    @bot.message_handler(func=lambda message: message.text.startswith('Тест: '))
    def handle_test_start(message):
        test_title = message.text.replace('Тест: ', '')
        tests = FirebaseDB.get_tests()
        test = next((t for t in tests if t['title'] == test_title), None)

        if not test:
            bot.send_message(message.chat.id, "Тест не найден")
            return

        bot.send_message(
            message.chat.id,
            f"📝 <b>{test['title']}</b>\n\n"
            f"{test.get('description', '')}\n\n"
            f"Проходной балл: {test['passing_score']} из {len(test['questions'])}\n\n"
            "Готовы начать тест?",
            parse_mode='HTML',
            reply_markup=types.ForceReply(selective=False)
        )
        bot.register_next_step_handler(message, start_test, test)

    def start_test(message, test):
        if message.text == '🔙 Назад':
            handle_testing(message)
            return

        user_id = message.from_user.id
        questions = test['questions']
        random.shuffle(questions)

        test_session = {
            'user_id': user_id,
            'test_id': test['id'],
            'questions': questions,
            'current_question': 0,
            'answers': [],
            'score': 0
        }

        ask_question(message, test_session)

    def ask_question(message, test_session):
        question_index = test_session['current_question']
        question = test_session['questions'][question_index]

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        options = question['options']
        random.shuffle(options)

        for option in options:
            markup.add(types.KeyboardButton(option))

        markup.add(types.KeyboardButton('🔙 Назад'))

        bot.send_message(
            message.chat.id,
            f"❓ Вопрос {question_index + 1} из {len(test_session['questions'])}\n\n"
            f"{question['text']}",
            reply_markup=markup
        )
        bot.register_next_step_handler(message, process_answer, test_session)

    def process_answer(message, test_session):
        if message.text == '🔙 Назад':
            handle_testing(message)
            return

        question_index = test_session['current_question']
        question = test_session['questions'][question_index]

        user_answer = message.text
        is_correct = user_answer == question['correct_answer']

        test_session['answers'].append({
            'question': question['text'],
            'user_answer': user_answer,
            'correct_answer': question['correct_answer'],
            'is_correct': is_correct
        })

        if is_correct:
            test_session['score'] += 1

        test_session['current_question'] += 1

        if test_session['current_question'] < len(test_session['questions']):
            ask_question(message, test_session)
        else:
            finish_test(message, test_session)

    def finish_test(message, test_session):
        test = FirebaseDB.get_test(test_session['test_id'])
        total_questions = len(test_session['questions'])
        score = test_session['score']
        passing_score = test['passing_score']
        passed = score >= passing_score

        result_data = {
            'user_id': test_session['user_id'],
            'test_id': test_session['test_id'],
            'score': score,
            'total_questions': total_questions,
            'passed': passed,
            'completion_date': datetime.now()
        }
        FirebaseDB.save_test_result(result_data)

        result_message = (
            f"📝 <b>Результаты теста: {test['title']}</b>\n\n"
            f"✅ Правильных ответов: {score} из {total_questions}\n"
            f"📊 Проходной балл: {passing_score}\n\n"
        )

        if passed:
            result_message += "🎉 <b>Поздравляем! Вы успешно прошли тест!</b>"
        else:
            result_message += "😞 К сожалению, вы не набрали проходной балл. Попробуйте еще раз!"

        bot.send_message(
            message.chat.id,
            result_message,
            parse_mode='HTML',
            reply_markup=create_back_button()
        )