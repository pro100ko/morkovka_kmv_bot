from telebot import types
from firebase_db import FirebaseDB
from firebase_admin import firestore
from config import Config
from utils.keyboard_utils import create_category_keyboard, create_products_keyboard, create_back_button


def register_knowledge_base_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == '📚 База знаний')
    def handle_knowledge_base(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('🗂 Категории товаров')
        btn2 = types.KeyboardButton('🔍 Поиск товара')
        btn_back = types.KeyboardButton('🔙 Назад')
        markup.add(btn1, btn2, btn_back)

        bot.send_message(
            message.chat.id,
            "📚 <b>База знаний</b>\n\n"
            "Здесь вы можете изучить информацию о товарах, которые продает наша компания.",
            parse_mode='HTML',
            reply_markup=markup
        )

    @bot.message_handler(func=lambda message: message.text == '🗂 Категории товаров')
    def handle_categories(message):
        categories = FirebaseDB.get_categories()
        if not categories:
            categories = [{'name': cat, 'id': idx} for idx, cat in enumerate(Config.PRODUCT_CATEGORIES)]

        markup = create_category_keyboard(categories)
        markup.add(types.KeyboardButton('🔙 Назад'))

        bot.send_message(
            message.chat.id,
            "🗂 <b>Категории товаров</b>\n\n"
            "Выберите категорию для просмотра товаров:",
            parse_mode='HTML',
            reply_markup=markup
        )

    @bot.message_handler(func=lambda message: message.text.startswith('Категория: '))
    def handle_category_products(message):
        category_name = message.text.replace('Категория: ', '')
        categories = FirebaseDB.get_categories()
        category = next((cat for cat in categories if cat['name'] == category_name), None)

        if not category:
            bot.send_message(message.chat.id, "Категория не найдена")
            return

        products = FirebaseDB.get_products_by_category(category['id'])
        if not products:
            bot.send_message(message.chat.id, f"В категории '{category_name}' пока нет товаров")
            return

        markup = create_products_keyboard(products)
        markup.add(types.KeyboardButton('🔙 Назад'))

        bot.send_message(
            message.chat.id,
            f"📦 <b>Товары категории: {category_name}</b>\n\n"
            "Выберите товар для просмотра подробной информации:",
            parse_mode='HTML',
            reply_markup=markup
        )

    @bot.message_handler(func=lambda message: message.text.startswith('Товар: '))
    def handle_product_info(message):
        product_name = message.text.replace('Товар: ', '')
        products = FirebaseDB.search_products(product_name)
        product = next((p for p in products if p['name'] == product_name), None)

        if not product:
            bot.send_message(message.chat.id, "Товар не найден")
            return

        category = FirebaseDB.get_category(product['category_id'])
        category_name = category['name'] if category else "Неизвестная категория"

        product_text = (
            f"📦 <b>{product['name']}</b>\n\n"
            f"🗂 Категория: {category_name}\n"
            f"📝 Описание: {product.get('description', 'Нет описания')}\n\n"
            f"🌡 Условия хранения: {product.get('storage_conditions', 'Не указаны')}\n"
            f"📅 Срок годности: {product.get('shelf_life', 'Не указан')}\n"
            f"💰 Цена: {product.get('price', 'Не указана')}"
        )

        if 'photo_url' in product:
            bot.send_photo(
                message.chat.id,
                product['photo_url'],
                caption=product_text,
                parse_mode='HTML',
                reply_markup=create_back_button()
            )
        else:
            bot.send_message(
                message.chat.id,
                product_text,
                parse_mode='HTML',
                reply_markup=create_back_button()
            )

    @bot.message_handler(func=lambda message: message.text == '🔍 Поиск товара')
    def handle_search(message):
        bot.send_message(
            message.chat.id,
            "🔍 <b>Поиск товара</b>\n\n"
            f"Введите название товара (минимум {Config.MIN_SEARCH_QUERY_LENGTH} символа):",
            parse_mode='HTML',
            reply_markup=create_back_button()
        )
        bot.register_next_step_handler(message, process_search_query)

    def process_search_query(message):
        if message.text == '🔙 Назад':
            handle_knowledge_base(message)
            return

        query = message.text.strip()
        if len(query) < Config.MIN_SEARCH_QUERY_LENGTH:
            bot.send_message(
                message.chat.id,
                f"Запрос слишком короткий. Минимальная длина: {Config.MIN_SEARCH_QUERY_LENGTH} символа"
            )
            return

        products = FirebaseDB.search_products(query)
        if not products:
            bot.send_message(message.chat.id, "Товары по вашему запросу не найдены")
            return

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for product in products[:Config.MAX_SEARCH_RESULTS]:
            markup.add(types.KeyboardButton(f"Товар: {product['name']}"))

        markup.add(types.KeyboardButton('🔙 Назад'))

        bot.send_message(
            message.chat.id,
            f"🔍 <b>Результаты поиска по запросу: '{query}'</b>\n\n"
            f"Найдено товаров: {len(products)}\n"
            f"Показано: {min(len(products), Config.MAX_SEARCH_RESULTS)}",
            parse_mode='HTML',
            reply_markup=markup
        )