from telebot import types

from config import ADMIN_ID
from database.db import get_db
from telebot.types import InputMediaPhoto
from bot_instance import bot
from database.db_operations import check_record_exists, get_products, update_order_status, process_item_image, \
    process_shop_status, process_edit_cat
from keyboards import create_main_keyboard

def send_product_page(call, photos, descr):
    media = []
    for i, photo_path in enumerate(photos):
        try:
            with open(photo_path, 'rb') as f:
                photo_data = f.read()
                if i == 0:
                    media.append(InputMediaPhoto(
                        media=photo_data,
                        caption=descr,
                        parse_mode="Markdown"
                    ))
                else:
                    media.append(InputMediaPhoto(media=photo_data))
        except Exception as e:
            print(f"Ошибка при открытии файла {photo_path}: {e}")

    if media:
        bot.send_media_group(call, media)
    else:
        bot.send_message(call, "Не удалось загрузить изображения.")

def process_fio_step(message):
    try:
        fio = message.text.strip()
        if len(fio) < 5:
            bot.send_message(message.chat.id, "Ошибка: ФИО слишком короткое! Минимум 5 символов.\nПопробуй ввести снова:")
            bot.register_next_step_handler(message, process_fio_step)
            return
        if len(fio) > 100:
            bot.send_message(message.chat.id, "Ошибка: ФИО слишком длинное! Максимум 100 символов.\nПопробуй ввести снова:")
            bot.register_next_step_handler(message, process_fio_step)
            return
        if not all(char.isalpha() or char in ' -\'' for char in fio.replace('ё', 'е').replace('Ё', 'Е')):
            bot.send_message(message.chat.id, "Ошибка: ФИО содержит недопустимые символы!\nПопробуй ввести снова:")
            bot.register_next_step_handler(message, process_fio_step)
            return

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET fio=? WHERE id=?", (fio, message.from_user.id))

        bot.send_message(message.chat.id, "ФИО успешно обновлено!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e} \nПопробуй ввести снова:")
        bot.register_next_step_handler(message, process_fio_step)

def process_phone_step(message):
    try:
        phone = message.text.strip()
        if phone[0] == '+' and len(phone) != 12:
            bot.send_message(message.chat.id, "Номер телефона введен некорректно! \nПопробуй ввести снова:")
            bot.register_next_step_handler(message, process_phone_step)
            return
        if phone[0] == '8' and len(phone) != 11:
            bot.send_message(message.chat.id, "Номер телефона введен некорректно!\nПопробуй ввести снова:")
            bot.register_next_step_handler(message, process_phone_step)
            return

        allowed_chars = set('0123456789+() -')
        if not all(char in allowed_chars for char in phone):
            bot.send_message(message.chat.id, "Ошибка: номер телефона содержит недопустимые символы!\nПопробуй ввести снова:")
            bot.register_next_step_handler(message, process_phone_step)
            return

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET phone_number=? WHERE id=?", (phone, message.from_user.id))

        bot.send_message(message.chat.id, "Номер телефона успешно обновлен!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПопробуй ввести снова:")
        bot.register_next_step_handler(message, process_phone_step)

def process_region_step(message):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET region=? WHERE id=?", (message.text, message.from_user.id))
        bot.send_message(message.chat.id, "Регион успешно обновлён!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПопробуй ввести снова:")
        bot.register_next_step_handler(message, process_region_step)

def process_city_step(message):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET city=? WHERE id=?", (message.text, message.from_user.id))
        bot.send_message(message.chat.id, "Город успешно обновлён!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПопробуй ввести снова:")
        bot.register_next_step_handler(message, process_city_step)

def process_street_step(message):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET street=? WHERE id=?", (message.text, message.from_user.id))
        bot.send_message(message.chat.id, "Улица успешно обновлена!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПопробуй ввести снова:")
        bot.register_next_step_handler(message, process_street_step)

def process_house_step(message):
    try:
        house = message.text.strip()
        if not house[0].isdigit() or len(house) > 15 or house[0] in "/\\":
            bot.send_message(message.chat.id, "Ошибка: номер дома введен некорректно!\nПопробуй ввести снова:")
            bot.register_next_step_handler(message, process_house_step)
            return
        allowed_chars = set('0123456789/\\абвгдежзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ- ')
        if not all(char in allowed_chars for char in house):
            bot.send_message(message.chat.id, "Ошибка: номер дома содержит недопустимые символы!\nПопробуй ввести снова:")
            bot.register_next_step_handler(message, process_house_step)
            return

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET house_number=? WHERE id=?", (house, message.from_user.id))

        bot.send_message(message.chat.id, "Номер дома успешно обновлён!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПопробуй ввести снова:")
        bot.register_next_step_handler(message, process_house_step)

def process_flat_step(message):
    try:
        if not message.text.isdigit():
            bot.send_message(message.chat.id, "Ошибка: номер квартиры должен быть числом!\nПопробуй ввести снова:")
            bot.register_next_step_handler(message, process_flat_step)
            return

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET flat_number=? WHERE id=?", (message.text, message.from_user.id))

        bot.send_message(message.chat.id, "Номер квартиры успешно обновлён!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПопробуй ввести снова:")
        bot.register_next_step_handler(message, process_flat_step)

def process_index_step(message):
    try:
        if not message.text.isdigit():
            bot.send_message(message.chat.id, "Ошибка: индекс должен содержать только цифры!\nПопробуй ввести снова:")
            bot.register_next_step_handler(message, process_index_step)
            return
        if len(message.text) != 6:
            bot.send_message(message.chat.id, "Ошибка: индекс должен содержать 6 цифр!\nПопробуй ввести снова:")
            bot.register_next_step_handler(message, process_index_step)
            return

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET [index]=? WHERE id=?", (message.text, message.from_user.id))

        bot.send_message(message.chat.id, "Индекс успешно обновлён!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПопробуй ввести снова:")
        bot.register_next_step_handler(message, process_index_step)

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
        if message.text.strip().lower() in ["отмена", "❌ отмена"]:
            bot.send_message(
                message.chat.id,
                "Куда дальше?🔥",
                reply_markup=create_main_keyboard()
            )
            return
        products = get_products()
        item_id = int(message.text.strip())
        if 1 <= item_id <= len(products):
            product = products[item_id - 1]
            user_id = message.from_user.id
            if product.status:
                markup = types.InlineKeyboardMarkup()
                send_product_page(message.chat.id, product.images, product.description)
                fav_callback = f'favorite{product.id}'
                if not check_record_exists(user_id, product.id):
                    fav_button = types.InlineKeyboardButton('❤️', callback_data=fav_callback)
                else:
                    fav_button = types.InlineKeyboardButton('🤍', callback_data=fav_callback)
                cart_button = types.InlineKeyboardButton('🛒', callback_data=f'cart{product.id}')
                markup.add(fav_button, cart_button)
                bot.send_message(message.chat.id, '⬇️⬇️⬇️', reply_markup=markup)
                bot.send_message(message.chat.id, 'Куда дальше?🔥', reply_markup = create_main_keyboard())

            else:
                send_product_page(message.chat.id, product.images, "*НЕТ В НАЛИЧИИ!*\n\n" + product.description)
                bot.send_message(message.chat.id, 'Куда дальше?🔥', reply_markup=create_main_keyboard())

        else:
            bot.send_message(message.chat.id, f"ID должен быть от 1 до {len(products)}")
            msg = bot.send_message(message.chat.id, "Попробуй ввести ID ещё раз:")
            bot.register_next_step_handler(msg, process_product_id_search)

    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введи число!")
        msg = bot.send_message(message.chat.id, "Попробуй ввести ID ещё раз:")
        bot.register_next_step_handler(msg, process_product_id_search)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

def is_admin(user_id):
    return user_id == ADMIN_ID

def process_edit_item(message):
    try:
        item_id = int(message.text)
        markup = types.InlineKeyboardMarkup()
        i1 = types.InlineKeyboardButton('Название', callback_data="admin_edit_item_name_"+str(item_id))
        i2 = types.InlineKeyboardButton('Описание', callback_data="admin_edit_item_description_" + str(item_id))
        i3 = types.InlineKeyboardButton('ID продавца', callback_data="admin_edit_item_shop_" + str(item_id))
        i4 = types.InlineKeyboardButton('ID категории', callback_data="admin_edit_item_category_" + str(item_id))
        i6 = types.InlineKeyboardButton('Цена', callback_data="admin_edit_item_price_" + str(item_id))
        i7 = types.InlineKeyboardButton('Картинки', callback_data="admin_edit_item_images_" + str(item_id))
        i8 = types.InlineKeyboardButton('Статус', callback_data="admin_edit_item_status_" + str(item_id))
        i9 = types.InlineKeyboardButton('Размеры', callback_data="admin_edit_item_sizes_" + str(item_id))
        markup.add(i1,i2,i3,i4,i6,i7,i8,i9)
        bot.send_message(message.chat.id, "Выберете поле, которое хотите изменить:", reply_markup=markup)

    except Exception as e:
        print(f"Error in process_order_id_for_status: {e}")

def process_edit_shop(message):
    try:
        item_id = int(message.text)
        markup = types.InlineKeyboardMarkup()
        i1 = types.InlineKeyboardButton('Название', callback_data="admin_edit_shop_name_"+str(item_id))
        i2 = types.InlineKeyboardButton('Описание', callback_data="admin_edit_shop_description_" + str(item_id))
        i3 = types.InlineKeyboardButton('Картинки', callback_data="admin_edit_shop_images_" + str(item_id))
        i4 = types.InlineKeyboardButton('Статус', callback_data="admin_edit_shop_status_" + str(item_id))
        markup.add(i1,i2,i3,i4)
        bot.send_message(message.chat.id, "Выберете поле, которое хотите изменить:", reply_markup=markup)

    except Exception as e:
        print(f"Error in process_order_id_for_status: {e}")

def process_order_id_for_status(message):
    try:
        order_id = int(message.text)
        result = update_order_status(order_id)
        bot.send_message(message.chat.id, result)
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат ID. Введите число.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при изменении статуса: {str(e)}")
        print(f"Error in process_order_id_for_status: {e}")

def process_item_name(message, temp_items):
    try:
        chat_id = message.chat.id
        temp_items[chat_id]['name'] = message.text
        msg = bot.send_message(chat_id, "Введите описание товара:")
        bot.register_next_step_handler(msg, lambda m: process_item_description(m, temp_items))
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

def process_item_description(message, temp_items):
    try:
        chat_id = message.chat.id
        temp_items[chat_id]['description'] = message.text
        msg = bot.send_message(chat_id, "Введите ID продавца (магазина):")
        bot.register_next_step_handler(msg, lambda m: process_item_shop_id(m, temp_items))

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

def process_item_shop_id(message, temp_items):
    try:
        chat_id = message.chat.id
        temp_items[chat_id]['shop_id'] = int(message.text)
        msg = bot.send_message(chat_id, "Введите ID категории:")
        bot.register_next_step_handler(msg, lambda m: process_item_category_id(m, temp_items))

    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число для ID продавца")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

def process_item_category_id(message, temp_items):
    try:
        chat_id = message.chat.id
        temp_items[chat_id]['category_id'] = int(message.text)
        msg = bot.send_message(chat_id, "Введите цену товара (в рублях):")
        bot.register_next_step_handler(msg, lambda m: process_item_price(m, temp_items))

    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число для ID категории")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

def process_item_price(message, temp_items):
    try:
        chat_id = message.chat.id
        temp_items[chat_id]['price'] = int(message.text)
        msg = bot.send_message(chat_id, "Введите доступные размеры через пробел (например: S M L). Если у вещи нет размера, введите -")
        bot.register_next_step_handler(msg, lambda m: process_item_sizes(m, temp_items))

    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число для цены")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")


def process_item_sizes(message, temp_items):
    try:
        chat_id = message.chat.id
        temp_items[chat_id]['sizes'] = message.text
        msg = bot.send_message(chat_id, "Введите статус товара (True/False):")
        bot.register_next_step_handler(msg, lambda m: process_item_status(m, temp_items))
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")


def process_item_status(message, temp_items):
    try:
        chat_id = message.chat.id
        status = message.text.strip()
        if status not in ['True', 'False']:
            raise ValueError("Статус должен быть 0 или 1")
        temp_items[chat_id]['status'] = message.text
        msg = bot.send_message(chat_id, "Напишите список изображений товара (через пробел). Например: media/51.jpg media/52.jpg media/53.jpg media/54.jpg")
        bot.register_next_step_handler(msg, lambda m: process_item_image(m, temp_items))

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

def process_shop_name(message, temp_items):
    try:
        chat_id = message.chat.id
        temp_items[chat_id]['name'] = message.text
        msg = bot.send_message(chat_id, "Введите описание магазина:")
        bot.register_next_step_handler(msg, lambda m: process_shop_description(m, temp_items))

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")


def process_shop_description(message, temp_items):
    try:
        chat_id = message.chat.id
        temp_items[chat_id]['description'] = message.text
        msg = bot.send_message(chat_id, "Напишите список изображений магазина (через пробел). Например: media/51.jpg media/52.jpg media/53.jpg media/54.jpg")
        bot.register_next_step_handler(msg, lambda m: process_shop_images(m, temp_items))

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

def process_shop_images(message, temp_items):
    try:
        chat_id = message.chat.id
        temp_items[chat_id]['images'] = message.text
        msg = bot.send_message(chat_id, "Введите статус магазина (True/False):")
        bot.register_next_step_handler(msg, lambda m: process_shop_status(m, temp_items))

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")


def process_get_cat_id(message):
    try:
        cat_id = message.text
        if not cat_id.isdigit():
            bot.send_message(message.chat.id, "ID категории должен быть числом!")
            return

        msg = bot.send_message(message.chat.id, "Введите новое название категории:")
        bot.register_next_step_handler(msg, lambda m: process_edit_cat(m, cat_id))

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

