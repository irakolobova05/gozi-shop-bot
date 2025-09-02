from telebot import types

def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("Продавцы"),
        types.KeyboardButton("Каталог")
    )
    markup.add(
        types.KeyboardButton("Избранное"),
        types.KeyboardButton("Корзина")
    )
    markup.add(types.KeyboardButton("Личные данные"), types.KeyboardButton("Поиск по id"))
    return markup

def create_inline_keyboard(buttons):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for text, callback_data in buttons:
        markup.add(types.InlineKeyboardButton(text, callback_data=callback_data))
    return markup

def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("Заказы"),
        types.KeyboardButton("Товары")
    )
    markup.add(
        types.KeyboardButton("Селлеры"),
        types.KeyboardButton("Пользователи")
    )
    markup.add(types.KeyboardButton("Категории"))
    return markup