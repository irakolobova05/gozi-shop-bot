from datetime import datetime
from random import choice
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import ADMIN_ID
from constants import variants
from keyboards import create_main_keyboard, create_inline_keyboard, admin_keyboard
from database.db_operations import update_cart_quantity, insert_highlight, delete_highlight, delete_cart, insert_users, \
    personal_data, get_products, get_shops, get_categories, cart_database, likes_database, check_record_exists, \
    insert_cart_with_size, insert_cart, get_all_orders, update_item_field, update_shop_field, get_all_users, \
    get_user_info, delete_user_info, process_edit_cat
from database.db import get_db
from bot_instance import bot
from utils import send_product_page, process_fio_step, process_phone_step, process_region_step, process_city_step, \
    process_street_step, process_house_step, process_flat_step, process_index_step, price_counter, print_personal_data, \
    process_product_id_search, is_admin, process_edit_item, process_order_id_for_status, process_item_name, \
    process_edit_shop, process_shop_name, process_get_cat_id
media_messages = {}
cart_messages = {}
total_price_messages = {}
user_states = {}

@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        bot.send_message(message.chat.id, "Hello Admin!!!", reply_markup = admin_keyboard())
    else:
        remove_markup = types.ReplyKeyboardRemove()
        bot.send_message(
            message.chat.id,
            "⛔ У вас нет доступа к этой команде",
            reply_markup=remove_markup
        )

@bot.message_handler(func=lambda msg: msg.text == "Заказы" and is_admin(msg.from_user.id))
def handle_orders(message):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Все заказы', callback_data="admin_ord")
    item2 = types.InlineKeyboardButton('Изменить статус', callback_data="admin_ord_status")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "📦 Раздел заказов", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Товары" and is_admin(msg.from_user.id))
def handle_products(message):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Редактировать', callback_data="admin_edit_item")
    item2 = types.InlineKeyboardButton('Добавить', callback_data="admin_add_item")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "🛍️ Раздел товаров", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Селлеры" and is_admin(msg.from_user.id))
def handle_products(message):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Редактировать', callback_data="admin_edit_shop")
    item2 = types.InlineKeyboardButton('Добавить', callback_data="admin_add_shop")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "🛍️ Продавцы", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Пользователи" and is_admin(msg.from_user.id))
def handle_products(message):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Смотреть', callback_data="admin_check_user")
    item2 = types.InlineKeyboardButton('Поиск по ID', callback_data="admin_search_user")
    item3 = types.InlineKeyboardButton('Удалить', callback_data="admin_delete_user")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Пользователи", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Категории" and is_admin(msg.from_user.id))
def handle_products(message):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Изменить', callback_data="admin_change_cat")
    markup.add(item1)
    bot.send_message(message.chat.id, "Категории", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin'))
def handle_orders_buttons(call):
    try:
        if call.data.startswith('admin_edit_item_'):
            parts = call.data.split('_')
            action = parts[3]
            item_id = int(parts[4]) if len(parts) > 3 else None
            if action == "name":
                msg = bot.send_message(call.message.chat.id, f"Введите новое название для товара ID {item_id}:")
                bot.register_next_step_handler(msg, lambda m: update_item_field(m, item_id, 'name'))
            elif action == "description":
                msg = bot.send_message(call.message.chat.id, f"Введите новое описание для товара ID {item_id}:")
                bot.register_next_step_handler(msg, lambda m: update_item_field(m, item_id, 'description'))
            elif action == "shop":
                msg = bot.send_message(call.message.chat.id, f"Введите новый ID продавца для товара ID {item_id}:")
                bot.register_next_step_handler(msg, lambda m: update_item_field(m, item_id, 'shop_id'))
            elif action == "category":
                msg = bot.send_message(call.message.chat.id, f"Введите новый ID категории для товара ID {item_id}:")
                bot.register_next_step_handler(msg, lambda m: update_item_field(m, item_id, 'category_id'))
            elif action == "price":
                msg = bot.send_message(call.message.chat.id, f"Введите новую цену для товара ID {item_id}:")
                bot.register_next_step_handler(msg, lambda m: update_item_field(m, item_id, 'price'))
            elif action == "images":
                msg = bot.send_message(call.message.chat.id,
                                       f"Введите список названий изображений для товара ID {item_id} (через пробел):")
                bot.register_next_step_handler(msg, lambda m: update_item_field(m, item_id, 'images'))
            elif action == "status":
                msg = bot.send_message(call.message.chat.id, f"Введите новый статус для товара с ID {item_id} (True, False):")
                bot.register_next_step_handler(msg, lambda m: update_item_field(m, item_id, 'status'))
            elif action == "sizes":
                msg = bot.send_message(call.message.chat.id,
                                       f"Введите доступные размеры для товара ID {item_id} через пробел:")
                bot.register_next_step_handler(msg, lambda m: update_item_field(m, item_id, 'sizes'))

        elif call.data.startswith('admin_edit_shop_'):
            parts = call.data.split('_')
            action = parts[3]
            item_id = int(parts[4]) if len(parts) > 3 else None
            if action == "name":
                msg = bot.send_message(call.message.chat.id, f"Введите новое название для магазина {item_id}:")
                bot.register_next_step_handler(msg, lambda m: update_shop_field(m, item_id, 'name'))

            elif action == "description":
                msg = bot.send_message(call.message.chat.id, f"Введите новое описание для магазина ID {item_id}:")
                bot.register_next_step_handler(msg, lambda m: update_shop_field(m, item_id, 'description'))

            elif action == "images":
                msg = bot.send_message(call.message.chat.id, f"Введите список названий для изображений магазина ID {item_id} (через пробел):")
                bot.register_next_step_handler(msg, lambda m: update_shop_field(m, item_id, 'description'))

            elif action == "status":
                msg = bot.send_message(call.message.chat.id,
                                       f"Введите новый статус для магазина с ID {item_id} (True, False):")
                bot.register_next_step_handler(msg, lambda m: update_shop_field(m, item_id, 'status'))

        elif call.data == "admin_ord":
            orders = get_all_orders(call.message)
            if not orders:
                bot.send_message(call.message.chat.id, "Нет заказов")
                return
            chunk_size = 3
            for i in range(0, len(orders), chunk_size):
                chunk = orders[i:i + chunk_size]
                bot.send_message(call.message.chat.id, "\n\n".join(chunk))


        elif call.data == "admin_search_user":
            msg = bot.send_message(call.message.chat.id, "Введите ID пользователя для поиска:")
            bot.register_next_step_handler(msg, get_user_info)

        elif call.data == "admin_delete_user":
            msg = bot.send_message(call.message.chat.id, "Введите ID пользователя для удаления:")
            bot.register_next_step_handler(msg, delete_user_info)

        elif call.data == "admin_check_user":
            users = get_all_users(call.message)
            if not users:
                bot.send_message(call.message.chat.id, "Нет пользователей")
                return
            chunk_size = 10
            for i in range(0, len(users), chunk_size):
                chunk = users[i:i + chunk_size]
                bot.send_message(call.message.chat.id, "\n\n".join(chunk))

        elif call.data == "admin_ord_status":
            msg = bot.send_message(call.message.chat.id, "Введите ID заказа для изменения статуса:")
            bot.register_next_step_handler(msg, process_order_id_for_status)

        elif call.data == "admin_edit_item":
            msg = bot.send_message(call.message.chat.id, "Введите ID товара для изменения данных о нем:")
            bot.register_next_step_handler(msg, process_edit_item)

        elif call.data == "admin_add_item":
            chat_id = call.message.chat.id
            temp_items = {}
            temp_items[chat_id] = {}
            msg = bot.send_message(chat_id, "Введите название товара:")
            bot.register_next_step_handler(msg, lambda m: process_item_name(m, temp_items))

        elif call.data == "admin_edit_shop":
            msg = bot.send_message(call.message.chat.id, "Введите ID магазина для изменения данных о нем:")
            bot.register_next_step_handler(msg, process_edit_shop)

        elif call.data == "admin_change_cat":
            msg = bot.send_message(call.message.chat.id, "Введите ID категории для изменения названия:")
            bot.register_next_step_handler(msg, process_get_cat_id)

        elif call.data == "admin_add_shop":
            chat_id = call.message.chat.id
            temp_items = {}
            temp_items[chat_id] = {}
            msg = bot.send_message(chat_id, "Введите название магазина:")
            bot.register_next_step_handler(msg, lambda m: process_shop_name(m, temp_items))

    except Exception as e:
        bot.send_message(call.message.chat.id, f"Произошла ошибка: {str(e)}")
        print(f"Error in handle_orders_buttons: {e}")

@bot.message_handler(commands=['start'])
def welcome(message):
    try:
        user_name = message.from_user.username
        user_first_name = message.from_user.first_name
        user_id = message.from_user.id
        # Экранируем спецсимволы MarkdownV2 вручную
        escaped_first_name = user_first_name.translate(str.maketrans({
            "_": r"\_",
            "*": r"\*",
            "[": r"\[",
            "]": r"\]",
            "(": r"\(",
            ")": r"\)",
            "~": r"\~",
            "`": r"\`",
            ">": r"\>",
            "#": r"\#",
            "+": r"\+",
            "-": r"\-",
            "=": r"\=",
            "|": r"\|",
            "{": r"\{",
            "}": r"\}",
            ".": r"\.",
            "!": r"\!"
        }))
        agree_markup = InlineKeyboardMarkup()
        agree_markup.add(InlineKeyboardButton("✅ Согласен", callback_data="agree"))
        bot.send_message(
            message.chat.id,
            text=f"""
Привет, {escaped_first_name}\! 👋\nМы — торговая площадка, специализирующаяся на поддержке начинающих дизайнеров streetwear одежды\. Здесь ты найдёшь эксклюзивные вещи от талантливых российских дизайнеров\.\n\n Покупая у нас, ты не просто обновляешь гардероб — ты поддерживаешь независимых творцов и становишься частью нашего сообщества\!\n\n
            """,
            parse_mode='MarkdownV2',
            reply_markup=agree_markup
        )
        insert_users(user_id, user_name)
    except Exception as e:
        print(f"Ошибка: {str(e)}")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.type == 'private':
        if message.text == 'Продавцы':
            buttons=[]
            shops = get_shops()
            for i in range(len(shops)):
                if shops[i].status == True:
                    buttons.append((shops[i].name, str(shops[i].id)))
            markup = create_inline_keyboard(buttons)
            bot.send_message(message.chat.id, 'Лови подборку наших магазинов — куда заглянем? 🛒', reply_markup=markup)

        elif message.text == 'Каталог':
            buttons = []
            categories = get_categories()
            for i in range(len(categories)):
                buttons.append((categories[i].name, 'k'+str(categories[i].id)))
            markup = create_inline_keyboard(buttons)
            bot.send_message(message.chat.id, 'Сегодня закупаемся?\nВыбирай категорию🛍️', reply_markup=markup)

        elif message.text == 'Избранное':
            products = get_products()
            bot.send_message(message.chat.id, '*Избранное* \nВсё, что зацепило 👀', parse_mode="Markdown")
            user_id = message.from_user.id
            fav_ind = likes_database(user_id)
            favorites = {}
            for i in range(len(fav_ind)):
                if products[fav_ind[i]-1].status:
                    favorites[fav_ind[i]] = products[fav_ind[i]-1]

            for i in favorites:
                media = []
                arr=favorites[i].images
                descr=favorites[i].description
                for j in range(len(arr)):
                    with open(arr[j], 'rb') as f:
                        if j == 0:
                            media.append(types.InputMediaPhoto(f.read(), caption=descr, parse_mode="Markdown"))
                        else:
                            media.append(types.InputMediaPhoto(f.read()))
                sent_media_messages = bot.send_media_group(message.chat.id, media)
                media_messages[i] = [msg.message_id for msg in sent_media_messages]
                markup = types.InlineKeyboardMarkup()
                name1 = 'del_iz' + str(favorites[i].id)
                name2 = 'cart' + str(favorites[i].id)
                item1 = types.InlineKeyboardButton('🤍', callback_data=name1)
                item2 = types.InlineKeyboardButton('🛒', callback_data=name2)
                markup.add(item1, item2)
                bot.send_message(message.chat.id, '⬇️⬇️⬇️', reply_markup=markup)

        elif message.text == 'Корзина':
            products = get_products()
            user_id = message.from_user.id
            cart_arr = cart_database(user_id)
            total_price = 0
            total_quantity = 0
            bot.send_message(message.chat.id, "*Корзина*\nВсё на месте, ждёт тебя 🛒", parse_mode="Markdown")
            for i in range(len(cart_arr)):
                media = []
                arr = products[cart_arr[i][0]-1].images
                total_price += products[cart_arr[i][0] - 1].price * cart_arr[i][2]
                total_quantity += cart_arr[i][2]
                if cart_arr[i][1] is not None:
                    descr = products[cart_arr[i][0]-1].description + "\n \n*Размер: *" + cart_arr[i][1] + "\n \n*Количество:* "+ str(cart_arr[i][2])
                else:
                    descr = products[cart_arr[i][0] - 1].description + "\n \n*Количество:* "+ str(cart_arr[i][2])

                for j in range(len(arr)):
                    with open(arr[j], 'rb') as f:
                        if j == 0:
                            media.append(types.InputMediaPhoto(f.read(), caption=descr, parse_mode="Markdown"))
                        else:
                            media.append(types.InputMediaPhoto(f.read()))

                sent_media_messages = bot.send_media_group(message.chat.id, media)
                key = f"{cart_arr[i][0]}_{cart_arr[i][1]}"  # Уникальный ключ: product_id + size
                cart_messages[key] = [msg.message_id for msg in sent_media_messages]
                markup = types.InlineKeyboardMarkup()
                name1 = 'delcart' + '_' + str(cart_arr[i][0]) + '_' + str(cart_arr[i][1])
                name2 = 'quantity+' + '_' + str(cart_arr[i][0]) + '_' + str(cart_arr[i][1]) + '_' + str(cart_arr[i][2])
                name3 = 'quantity-' + '_' + str(cart_arr[i][0]) + '_' + str(cart_arr[i][1]) + '_' + str(cart_arr[i][2])
                item1 = types.InlineKeyboardButton('Удалить', callback_data=name1)
                item2 = types.InlineKeyboardButton('+', callback_data=name2)
                item3 = types.InlineKeyboardButton('-', callback_data=name3)
                markup.add(item1, item2, item3)
                delete_message = bot.send_message(message.chat.id, '⬇️⬇️⬇️', reply_markup=markup)
                cart_messages[key].append(delete_message.message_id)
            if total_quantity != 0 and total_price != 0:
                total_message = price_counter(message.chat.id, total_quantity, total_price)
                total_price_messages[message.chat.id] = total_message.message_id
            else:
                bot.send_message(message.chat.id, "Корзина пуста!")

        elif message.text == "Личные данные":
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("UPDATE users SET username=? WHERE id=?",
                            (message.from_user.username, message.from_user.id))
                conn.commit()
                user_id = message.from_user.id
                pers_data = personal_data(user_id)
                if not pers_data:  # Проверяем, есть ли данные
                    bot.send_message(message.chat.id, "Данные не найдены", parse_mode="Markdown")
                else:
                    txt=print_personal_data(pers_data)
                    markup = types.InlineKeyboardMarkup()
                    item1 = types.InlineKeyboardButton('Изменить данные', callback_data='change')
                    markup.add(item1)
                    bot.send_message(message.chat.id, txt, parse_mode="Markdown", reply_markup=markup)

        elif message.text == "Поиск по id":
            cancel_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            cancel_markup.add("❌ Отмена")
            msg = bot.send_message(message.chat.id, f"Заинтересовало что-то конкретное?🔥\nВведи ID товара, попробуем найти! (1-{len(get_products())}):", reply_markup=cancel_markup)
            bot.register_next_step_handler(msg, process_product_id_search)
        else:
            bot.send_message(message.chat.id, 'Я тебя не понимаю. Пожалуйста, выбери один из вариантов.')

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            user_id = call.from_user.id
            shops = get_shops()
            categories = get_categories()
            products = get_products()

            # изменить данные
            if call.data=="change":
                markup = types.InlineKeyboardMarkup()
                item2 = types.InlineKeyboardButton('ФИО', callback_data='change2')
                item3 = types.InlineKeyboardButton('Номер телефона', callback_data='change3')
                item4 = types.InlineKeyboardButton('Регион', callback_data='change4')
                item5 = types.InlineKeyboardButton('Город', callback_data='change5')
                item6 = types.InlineKeyboardButton('Улица', callback_data='change6')
                item7 = types.InlineKeyboardButton('Номер дома', callback_data='change7')
                item8 = types.InlineKeyboardButton('Номер квартиры', callback_data='change8')
                item9 = types.InlineKeyboardButton('Индекс', callback_data='change9')
                markup.add(item2, item3, item4, item5, item6, item7, item8, item9)
                bot.send_message(call.message.chat.id, "Выбери поле, у которого хочешь изменить значение", reply_markup=markup)

            elif call.data == 'change2':  # ФИО
                msg = bot.send_message(call.message.chat.id, "Введи новое ФИО:")
                bot.register_next_step_handler(msg, process_fio_step)

            elif call.data == 'change3':  # Номер телефона
                msg = bot.send_message(call.message.chat.id, "Введи новый номер телефона:")
                bot.register_next_step_handler(msg, process_phone_step)

            elif call.data == 'change4':  # Регион
                msg = bot.send_message(call.message.chat.id, "Введи новый регион:")
                bot.register_next_step_handler(msg, process_region_step)

            elif call.data == 'change5':  # Город
                msg = bot.send_message(call.message.chat.id, "Введи новый город:")
                bot.register_next_step_handler(msg, process_city_step)

            elif call.data == 'change6':  # Улица
                msg = bot.send_message(call.message.chat.id, "Введи новую улицу:")
                bot.register_next_step_handler(msg, process_street_step)

            elif call.data == 'change7':  # Номер дома
                msg = bot.send_message(call.message.chat.id, "Введи новый номер дома:")
                bot.register_next_step_handler(msg, process_house_step)

            elif call.data == 'change8':  # Номер квартиры
                msg = bot.send_message(call.message.chat.id, "Введи новый номер квартиры:")
                bot.register_next_step_handler(msg, process_flat_step)

            elif call.data == 'change9':  # Индекс
                msg = bot.send_message(call.message.chat.id, "Введи новый индекс:")
                bot.register_next_step_handler(msg, process_index_step)

            if call.data == "agree":
                try:
                    markup = create_main_keyboard()
                    bot.send_message(call.message.chat.id, "Теперь тебе доступен весь функционал нашего бота! С чего начнем?", reply_markup=markup)
                except Exception as e:
                    print(f"Ошибка в send_main_keyboard: {e}")

            if call.data == 'order':
                pers_data = personal_data(user_id)
                if pers_data is None:
                    bot.send_message(call.message.chat.id,
                                     'Не удалось получить твои данные. Пожалуйста, попробуй позже.')
                    return
                # Проверяем обязательные поля
                required_fields = {
                    3: 'ФИО',
                    1: 'Номер телефона',
                    8: 'Регион',
                    4: 'Город',
                    5: 'Улица',
                    6: 'Номер дома',
                    2: 'Индекс'
                }
                missing_fields = [field_name for index, field_name in required_fields.items()
                                  if len(pers_data) <= index or pers_data[index] is None]
                if missing_fields:
                    markup = types.InlineKeyboardMarkup()
                    message = 'Данных для заказа недостаточно! Не заполнены:\n' + \
                              '\n'.join(f'• {field}' for field in missing_fields) + \
                              '\n\nПожалуйста, введи недостающие данные.'
                    item = types.InlineKeyboardButton('Ввести', callback_data='change')
                    markup.add(item)
                    bot.send_message(call.message.chat.id, message, reply_markup=markup)
                    print_personal_data(pers_data)
                else:
                    bot.send_message(call.message.chat.id, 'Проверь корректность введенных данных:')
                    txt = print_personal_data(pers_data)
                    markup = types.InlineKeyboardMarkup()
                    item1 = types.InlineKeyboardButton('Изменить данные', callback_data='change')
                    item2 = types.InlineKeyboardButton('Все верно', callback_data='ok')
                    markup.add(item1, item2)
                    bot.send_message(call.message.chat.id, txt, parse_mode="Markdown", reply_markup=markup)

            if call.data == 'ok':
                try:
                    cart = cart_database(user_id)
                    today = datetime.now().strftime("%Y-%m-%d %H:%M")
                    if not cart:
                        bot.send_message(call.message.chat.id, "Корзина пуста!")
                        return
                    # Переносим товары из корзины в заказы
                    with get_db() as conn:
                        cur = conn.cursor()
                        for product_id, size, quantity in cart:
                            cur.execute("SELECT shop_id, price FROM products WHERE id = ?", (product_id,))
                            result = cur.fetchone()
                            if not result:
                                continue
                            shop_id, price = result
                            total_price = price * quantity
                            # Добавляем заказ
                            cur.execute('''
                                INSERT INTO orders (user_id, shop_id, product_id, date, quantity, size, price)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (user_id, shop_id, product_id, today, quantity, size, total_price))
                        cur.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
                    bot.send_message(call.message.chat.id,
                                     "✅ Спасибо за заказ! Наш менеджер свяжется с тобой в ближайшее время.")
                except Exception as e:
                    print(f"Ошибка при оформлении заказа: {e}")
                    bot.send_message(call.message.chat.id,
                                     "⚠️ Произошла ошибка при оформлении заказа. Пожалуйста, попробуй позже.")

            for i in range(len(shops)):
                if call.data==str(shops[i].id) and shops[i].status:
                    markup = types.InlineKeyboardMarkup()
                    name='next'+str(shops[i].id)
                    item = types.InlineKeyboardButton('Гоу', callback_data=name)
                    send_product_page(call.message.chat.id, shops[i].images, shops[i].description)
                    markup.add(item)
                    bot.send_message(call.message.chat.id, 'За покупками?🛍️', reply_markup=markup)
                    break

            #вывод товаров по магазинам
            for i in range(len(shops)):
                if call.data == 'next' + str(shops[i].id):
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    with get_db() as conn:
                        cur = conn.cursor()
                        cur.execute("SELECT id FROM products WHERE shop_id = ?", (shops[i].id,))
                        shop_pr = [row[0] for row in cur.fetchall()]

                    for product_id in shop_pr:
                        product_index = product_id - 1
                        product = products[product_index]
                        if product.status:
                            markup = types.InlineKeyboardMarkup()
                            fav_callback = f'favorite{product.id}'
                            if not check_record_exists(user_id, product.id):
                                fav_button = types.InlineKeyboardButton('❤️', callback_data=fav_callback)
                            else:
                                fav_button = types.InlineKeyboardButton('🤍', callback_data=fav_callback)
                            cart_button = types.InlineKeyboardButton('🛒', callback_data=f'cart{product.id}')
                            send_product_page(call.message.chat.id, product.images, product.description)
                            markup.add(fav_button, cart_button)
                            text = choice(variants)
                            bot.send_message(call.message.chat.id, text, reply_markup=markup)
                    break

            # вывод товаров по категориям
            for i in range(len(categories)):
                if call.data == 'k'+str(categories[i].id):
                    with get_db() as conn:
                        cur = conn.cursor()
                        cur.execute("SELECT id FROM products WHERE category_id = ?", (categories[i].id,))
                        prod = [row[0] for row in cur.fetchall()]

                    bot.send_message(call.message.chat.id, '*'+categories[i].name+ ':*', parse_mode="Markdown")
                    for product_id in prod:
                        product_index = product_id - 1
                        product = products[product_index]

                        if product.status:
                            markup = types.InlineKeyboardMarkup()
                            fav_callback = f'favorite{product.id}'
                            if not check_record_exists(user_id, product.id):
                                fav_button = types.InlineKeyboardButton('❤️', callback_data=fav_callback)
                            else:
                                fav_button = types.InlineKeyboardButton('🤍', callback_data=fav_callback)
                            cart_button = types.InlineKeyboardButton('🛒', callback_data=f'cart{product.id}')
                            send_product_page(call.message.chat.id, product.images, product.description)
                            markup.add(fav_button, cart_button)
                            text = choice(variants)
                            bot.send_message(call.message.chat.id, text, reply_markup=markup)
                    break

            # удалить из избранного
            for i in range(len(products)):
                if call.data == 'del_iz' + str(products[i].id):
                    favorite_id = products[i].id
                    if favorite_id in media_messages:
                        for message_id in media_messages[favorite_id]:
                            bot.delete_message(call.message.chat.id, message_id)

                        bot.delete_message(call.message.chat.id, call.message.message_id)
                    delete_highlight(user_id, products[i].id)
                    break

            # добавить в избранное
            for i in range(len(products)):
                if call.data == 'favorite' + str(products[i].id):
                    current_text = call.message.reply_markup.keyboard[0][0].text
                    new_button_text = '🤍' if current_text == '❤️' else '❤️'

                    markup = types.InlineKeyboardMarkup()
                    item1 = types.InlineKeyboardButton(new_button_text, callback_data=f'favorite{products[i].id}')
                    item2 = types.InlineKeyboardButton('🛒', callback_data=f'cart{products[i].id}')
                    markup.add(item1, item2)

                    bot.edit_message_reply_markup(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=markup
                    )

                    if new_button_text == '🤍':
                        bot.send_message(
                            chat_id=call.message.chat.id,
                            text='Добавил в избранное! Теперь не потеряется 🔖',
                            reply_to_message_id=call.message.message_id
                        )
                        insert_highlight(call.from_user.id, products[i].id)
                    else:
                        bot.send_message(
                            chat_id=call.message.chat.id,
                            text='Товар удалён из избранного!',
                            reply_to_message_id=call.message.message_id
                        )
                        delete_highlight(user_id, products[i].id)
                    break

            # добавить в корзину
            for i in range(len(products)):
                if call.data.startswith('cart'):
                    product_id = int(call.data.replace('cart', ''))
                    if products[i].id == product_id:
                        # Если у товара есть размеры
                        if hasattr(products[i], 'sizes') and products[i].sizes:
                            markup = types.InlineKeyboardMarkup()
                            for s in range(len(products[i].sizes)):
                                size = products[i].sizes[s]
                                name = 'sizecart' + '-' + f"{products[i].id}-{s}"
                                item = types.InlineKeyboardButton(size, callback_data=name)
                                markup.add(item)
                            bot.send_message(
                                chat_id=call.message.chat.id,
                                text='Выбери размер',
                                reply_to_message_id=call.message.message_id,
                                reply_markup=markup
                            )
                        else:
                            # Если размеров нет, добавляем товар в корзину
                            insert_cart(user_id, products[i].id)
                            bot.send_message(
                                chat_id=call.message.chat.id,
                                text="Готово! Лут в корзине — почти твой 😉",
                                reply_to_message_id=call.message.message_id
                            )
                        break

                elif call.data.startswith('sizecart'):
                    r = call.data.split('-')
                    product_id = int(r[1])
                    size_index = int(r[2])
                    if products[i].id == product_id:
                        # Добавляем товар с выбранным размером в корзину
                        insert_cart_with_size(user_id, products[i].id, products[i].sizes[size_index])
                        bot.send_message(
                            chat_id=call.message.chat.id,
                            text="Готово! Лут в корзине — почти твой 😉",
                            reply_to_message_id=call.message.message_id
                        )
                        break

            # удалить из корзины
            if call.data.startswith('delcart'):
                try:
                    r = call.data.split('_')
                    product_id = int(r[1])
                    size = r[2]
                    key = f"{product_id}_{size}"
                    if key in cart_messages:
                        for message_id in cart_messages[key]:
                            try:
                                bot.delete_message(call.message.chat.id, message_id)
                            except Exception as e:
                                print(f"Ошибка при удалении сообщения {message_id}: {e}")
                        del cart_messages[key]
                    if size != 'None':
                        delete_cart(user_id, product_id, size)
                    else:
                        delete_cart(user_id, product_id)
                    with get_db() as conn:
                        cur = conn.cursor()
                        cur.execute("""
                                    SELECT 
                                        SUM(c.quantity), 
                                        SUM(c.quantity * p.price) 
                                    FROM cart c
                                    JOIN products p ON c.product_id = p.id
                                    WHERE c.user_id = ?
                                """, (user_id,))
                        new_quantity, new_price = cur.fetchone()

                    if call.message.chat.id in total_price_messages:
                        try:
                            bot.delete_message(call.message.chat.id, total_price_messages[call.message.chat.id])
                        except:
                            pass
                    if new_quantity and new_price:
                        total_message = price_counter(call.message.chat.id,
                                                      new_quantity if new_quantity else 0,
                                                      new_price if new_price else 0.0)
                        total_price_messages[call.message.chat.id] = total_message.message_id
                    else:
                        bot.send_message(call.message.chat.id, "Корзина пуста!")

                except Exception as e:
                    print(f"Ошибка в обработке delcart: {e}")

            if call.data.startswith('quantity+'):
                try:
                    r = call.data.split('_')
                    if len(r) < 4:
                        print(f"Неверный формат callback_data: {call.data}")
                        return

                    product_id = int(r[1])
                    size = r[2]
                    quantity = int(r[3])
                    key = f"{product_id}_{size}"

                    if size != 'None':
                        update_cart_quantity(user_id, product_id, size, quantity + 1)
                    else:
                        update_cart_quantity(user_id, product_id, None, quantity + 1)

                    if key in cart_messages:
                        for message_id in cart_messages[key]:
                            try:
                                bot.delete_message(call.message.chat.id, message_id)
                            except Exception as e:
                                print(f"Ошибка при удалении сообщения {message_id}: {e}")

                        del cart_messages[key]

                    media = []
                    arr = products[product_id - 1].images
                    if size != 'None':
                        descr = products[
                                    product_id - 1].description + "\n \n*Размер: *" + size + "\n \n*Количество:* " + str(
                            quantity + 1)
                    else:
                        descr = products[product_id - 1].description + "\n \n*Количество:* " + str(quantity + 1)

                    for j in range(len(arr)):
                        with open(arr[j], 'rb') as f:
                            if j == 0:
                                media.append(types.InputMediaPhoto(f.read(), caption=descr, parse_mode="Markdown"))
                            else:
                                media.append(types.InputMediaPhoto(f.read()))

                    sent_media_messages = bot.send_media_group(call.message.chat.id, media)
                    key = f"{product_id}_{size}"
                    cart_messages[key] = [msg.message_id for msg in sent_media_messages]

                    markup = types.InlineKeyboardMarkup()
                    name1 = 'delcart' + '_' + str(product_id) + '_' + str(size) + '_' + str(quantity + 1)
                    name2 = 'quantity+' + '_' + str(product_id) + '_' + str(size) + '_' + str(quantity + 1)
                    name3 = 'quantity-' + '_' + str(product_id) + '_' + str(size) + '_' + str(quantity + 1)
                    item1 = types.InlineKeyboardButton('Удалить', callback_data=name1)
                    item2 = types.InlineKeyboardButton('+', callback_data=name2)
                    item3 = types.InlineKeyboardButton('-', callback_data=name3)
                    markup.add(item1, item2, item3)
                    delete_message = bot.send_message(call.message.chat.id, '⬇️⬇️⬇️', reply_markup=markup)
                    cart_messages[key].append(delete_message.message_id)
                    # Получаем актуальные данные корзины
                    with get_db() as conn:
                        cur = conn.cursor()
                        cur.execute("""
                                                SELECT 
                                                    SUM(c.quantity), 
                                                    SUM(c.quantity * p.price) 
                                                FROM cart c
                                                JOIN products p ON c.product_id = p.id
                                                WHERE c.user_id = ?
                                            """, (user_id,))
                        new_quantity, new_price = cur.fetchone()

                    if call.message.chat.id in total_price_messages:
                        try:
                            bot.delete_message(call.message.chat.id, total_price_messages[call.message.chat.id])
                        except:
                            pass
                    # Обновляем счетчик
                    if new_quantity != 0 and new_price != 0:
                        total_message = price_counter(call.message.chat.id,
                                                      new_quantity if new_quantity else 0,
                                                      new_price if new_price else 0.0)
                        total_price_messages[call.message.chat.id] = total_message.message_id
                    else:
                        bot.send_message(call.message.chat.id, "Корзина пуста!")
                except Exception as e:
                    print(f"Ошибка в обработке quantity+: {e}")

            #уменьшить кол-во
            if call.data.startswith('quantity-'):
                try:
                    r = call.data.split('_')
                    if len(r) < 4:
                        print(f"Неверный формат callback_data: {call.data}")
                        return

                    product_id = int(r[1])
                    size = r[2]
                    quantity = int(r[3])
                    key = f"{product_id}_{size}"

                    if quantity >= 2:
                        # Уменьшаем количество в корзине
                        if size != 'None':
                            update_cart_quantity(user_id, product_id, size, quantity - 1)
                        else:
                            update_cart_quantity(user_id, product_id, None, quantity - 1)

                        if key in cart_messages:
                            for message_id in cart_messages[key]:
                                try:
                                    bot.delete_message(call.message.chat.id, message_id)
                                except Exception as e:
                                    print(f"Ошибка при удалении сообщения {message_id}: {e}")

                            del cart_messages[key]

                        media = []
                        arr = products[product_id - 1].images
                        if size != 'None':
                            descr = products[
                                        product_id - 1].description + "\n \n*Размер: *" + size + "\n \n*Количество:* " + str(
                                quantity - 1)
                        else:
                            descr = products[product_id - 1].description + "\n \n*Количество:* " + str(quantity - 1)

                        for j in range(len(arr)):
                            with open(arr[j], 'rb') as f:
                                if j == 0:
                                    media.append(types.InputMediaPhoto(f.read(), caption=descr, parse_mode="Markdown"))
                                else:
                                    media.append(types.InputMediaPhoto(f.read()))

                        sent_media_messages = bot.send_media_group(call.message.chat.id, media)
                        key = f"{product_id}_{size}"
                        cart_messages[key] = [msg.message_id for msg in sent_media_messages]

                        markup = types.InlineKeyboardMarkup()
                        name1 = 'delcart' + '_' + str(product_id) + '_' + str(size) + '_' + str(quantity - 1)
                        name2 = 'quantity+' + '_' + str(product_id) + '_' + str(size) + '_' + str(quantity - 1)
                        name3 = 'quantity-' + '_' + str(product_id) + '_' + str(size) + '_' + str(quantity - 1)
                        item1 = types.InlineKeyboardButton('Удалить', callback_data=name1)
                        item2 = types.InlineKeyboardButton('+', callback_data=name2)
                        item3 = types.InlineKeyboardButton('-', callback_data=name3)
                        markup.add(item1, item2, item3)
                        delete_message = bot.send_message(call.message.chat.id, '⬇️⬇️⬇️', reply_markup=markup)
                        cart_messages[key].append(delete_message.message_id)
                        # Получаем актуальные данные корзины
                        with get_db() as conn:
                            cur = conn.cursor()
                            cur.execute("""
                                                    SELECT 
                                                        SUM(c.quantity), 
                                                        SUM(c.quantity * p.price) 
                                                    FROM cart c
                                                    JOIN products p ON c.product_id = p.id
                                                    WHERE c.user_id = ?
                                                """, (user_id,))
                            new_quantity, new_price = cur.fetchone()

                        if call.message.chat.id in total_price_messages:
                            try:
                                bot.delete_message(call.message.chat.id, total_price_messages[call.message.chat.id])
                            except:
                                pass
                        # Обновляем счетчик
                        if new_quantity != 0 and new_price != 0:
                            total_message = price_counter(call.message.chat.id,
                                                          new_quantity if new_quantity else 0,
                                                          new_price if new_price else 0.0)
                            total_price_messages[call.message.chat.id] = total_message.message_id
                        else:
                            bot.send_message(call.message.chat.id, "Корзина пуста!")
                except Exception as e:
                    print(f"Ошибка в обработке quantity-: {e}")
    except Exception as e:
        print(repr(e))

# Запуск бота
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, skip_pending=True)
        except Exception as e:
            print(f"Ошибка при polling: {e}")

