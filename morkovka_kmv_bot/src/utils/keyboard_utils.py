from telebot import types
from src.config import Config

def create_category_keyboard(categories):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for category in categories:
        markup.add(types.KeyboardButton(f"Категория: {category['name']}"))
    return markup

def create_products_keyboard(products):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for product in products:
        markup.add(types.KeyboardButton(f"Товар: {product['name']}"))
    return markup

def create_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton('📊 Статистика пользователей')
    btn2 = types.KeyboardButton('➕ Добавить товар')
    btn3 = types.KeyboardButton('📝 Создать тест')
    markup.add(btn1, btn2, btn3)
    return markup

def create_back_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('🔙 Назад')
    markup.add(btn)
    return markup