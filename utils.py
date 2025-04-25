from telebot import types

from telebot.types import InputMediaPhoto
from bot_instance import bot
from database.db_operations import check_record_exists, get_products


def send_product_page(call, photos, descr):
    media = []
    for i, photo in enumerate(photos):
        if i == 0:
            media.append(InputMediaPhoto(
                media=open(photo, 'rb'),
                caption=descr,
                parse_mode="Markdown"
            ))
        else:
            media.append(InputMediaPhoto(
                media=open(photo, 'rb')
            ))

    bot.send_media_group(call, media)


def process_fio_step(message, conn):
    cursor = conn.cursor()
    try:
        fio = message.text.strip()

        # Проверка минимальной и максимальной длины
        if len(fio) < 5:
            bot.send_message(message.chat.id, "Ошибка: ФИО слишком короткое! Минимум 5 символов.")
            return
        if len(fio) > 100:
            bot.send_message(message.chat.id, "Ошибка: ФИО слишком длинное! Максимум 100 символов.")
            return

        # Проверка на допустимые символы (русские буквы, дефисы, пробелы, апострофы)
        if not all(char.isalpha() or char in ' -\'' for char in fio.replace('ё', 'е').replace('Ё', 'Е')):
            bot.send_message(message.chat.id,
                             "Ошибка: ФИО содержит недопустимые символы! Можно использовать только буквы, пробелы и дефисы.")
            return

        cursor.execute("UPDATE users SET fio=? WHERE id=?",
                      (message.text, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, "ФИО успешно обновлено!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


def process_phone_step(message, conn):
    cursor = conn.cursor()
    try:
        if message.text[0]=='+' and len(message.text)!=12:
            bot.send_message(message.chat.id, "Номер телефона введен некорректно!")
            return
        if message.text[0]=='8' and len(message.text)!=11:
            bot.send_message(message.chat.id, "Номер телефона введен некорректно!")
            return
        allowed_chars = set(
            '0123456789+() -')
        if not all(char in allowed_chars for char in message.text):
            bot.send_message(message.chat.id, "Ошибка: номер телефона содержит недопустимые символы!")
            return

        cursor.execute("UPDATE users SET phone_number=? WHERE id=?",
                      (message.text, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, "Номер телефона успешно обновлен!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


def process_region_step(message, conn):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET region=? WHERE id=?",
                      (message.text, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, "Регион успешно обновлен!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


def process_city_step(message, conn):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET city=? WHERE id=?",
                      (message.text, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, "Город успешно обновлен!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


def process_street_step(message, conn):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET street=? WHERE id=?",
                      (message.text, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, "Улица успешно обновлена!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


def process_house_step(message, conn):
    cursor = conn.cursor()
    try:
        if not message.text[0].isdigit() or len(message.text) > 15 or message.text[0] in "/\\":
            bot.send_message(message.chat.id, "Ошибка: номер дома введен некорректно!")
            return
        allowed_chars = set(
            '0123456789/\\абвгдежзийклмнопрстуфхцчшщъыьэюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ- ')
        if not all(char in allowed_chars for char in message.text):
            bot.send_message(message.chat.id, "Ошибка: номер дома содержит недопустимые символы!")
            return

        cursor.execute("UPDATE users SET house_number=? WHERE id=?",
                      (message.text, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, "Номер дома успешно обновлен!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


def process_flat_step(message, conn):
    cursor = conn.cursor()
    try:
        if not message.text.isdigit():
            bot.send_message(message.chat.id, "Ошибка: номер квартиры должен быть числом!")
            return
        cursor.execute("UPDATE users SET flat_number=? WHERE id=?",
                      (message.text, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, "Номер квартиры успешно обновлен!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")


def process_index_step(message, conn):
    cursor = conn.cursor()
    try:
        if not message.text.isdigit():
            bot.send_message(message.chat.id, "Ошибка: индекс должен содержать только цифры!")
            return

        if len(message.text) != 6:
            bot.send_message(message.chat.id, "Ошибка: индекс должен содержать 6 цифр!")
            return

            # Если проверки пройдены, обновляем данные
        cursor.execute("UPDATE users SET [index]=? WHERE id=?",
                       (message.text, message.from_user.id))
        conn.commit()
        bot.send_message(message.chat.id, "Индекс успешно обновлен!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

def price_counter(mess, total_q, total_p):
    if total_q % 10 == 1 and total_q % 100 != 11:
        goods_word = "товар"
    elif 2 <= total_q % 10 <= 4 and (total_q % 100 < 10 or total_q % 100 >= 20):
        goods_word = "товара"
    else:
        goods_word = "товаров"

    mes = "В корзине " + str(total_q) + " " + goods_word + " на сумму " + str(total_p) + " рублей."

    mar = types.InlineKeyboardMarkup()
    i1 = types.InlineKeyboardButton('Оформить заказ', callback_data="order")
    mar.add(i1)
    total_mes = bot.send_message(mess, mes, reply_markup=mar)
    return total_mes

def print_personal_data(pers_data):
    descr = (
        f"*Username: *{pers_data[0] if pers_data[0] is not None else '-'}\n"
        f"*ФИО: *{pers_data[3] if pers_data[3] is not None else '-'}\n"
        f"*Номер телефона: *{pers_data[1] if pers_data[1] is not None else '-'}\n"
        f"*Регион: *{pers_data[8] if pers_data[8] is not None else '-'}\n"
        f"*Город: *{pers_data[4] if pers_data[4] is not None else '-'}\n"
        f"*Улица: *{pers_data[5] if pers_data[5] is not None else '-'}\n"
        f"*Номер дома: *{pers_data[6] if pers_data[6] is not None else '-'}\n"
        f"*Номер квартиры: *{pers_data[7] if pers_data[7] is not None else '-'}\n"
        f"*Индекс: *{pers_data[2] if pers_data[2] is not None else '-'}"
    )

    txt = "*Личные данные:* \n\n" + descr
    return txt


def process_product_id_search(message):
    try:
        products = get_products()
        item_id = int(message.text.strip())

        if 1 <= item_id <= len(products):
            product = products[item_id - 1]
            user_id = message.from_user.id


            if product.status:
                markup = types.InlineKeyboardMarkup()
                send_product_page(message.chat.id, product.images, product.description)
                # Кнопка избранного
                fav_callback = f'favorite{product.id}'
                if not check_record_exists(user_id, product.id):
                    fav_button = types.InlineKeyboardButton('❤️', callback_data=fav_callback)
                else:
                    fav_button = types.InlineKeyboardButton('🤍', callback_data=fav_callback)

                # Кнопка корзины
                cart_button = types.InlineKeyboardButton('🛒', callback_data=f'cart{product.id}')

                # Отправка продукта

                markup.add(fav_button, cart_button)
                bot.send_message(message.chat.id, '⬇️⬇️⬇️', reply_markup=markup)
            else:
                send_product_page(message.chat.id, product.images, "*НЕТ В НАЛИЧИИ!*\n\n" + product.description)

        else:
            bot.send_message(message.chat.id, f"ID должен быть от 1 до {len(products)}")
            # Предлагаем попробовать снова
            msg = bot.send_message(message.chat.id, "Попробуй ввести ID ещё раз:")
            bot.register_next_step_handler(msg, process_product_id_search)

    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введи число!")
        # Предлагаем попробовать снова
        msg = bot.send_message(message.chat.id, "Попробуй ввести ID ещё раз:")
        bot.register_next_step_handler(msg, process_product_id_search)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")