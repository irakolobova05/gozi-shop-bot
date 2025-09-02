import sqlite3
from bot_instance import bot
from database.db import get_db
from models import Category, Shop, Product

def update_cart_quantity(us_id: int, product_id: int, size: str, quantity: int):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            if size:
                cur.execute(
                    'UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ? AND size = ?',
                    (quantity, us_id, product_id, size)
                )
            else:
                cur.execute(
                    'UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ? AND size IS NULL',
                    (quantity, us_id, product_id)
                )
            conn.commit()
    except sqlite3.Error as e:
        print(f"[update_cart_quantity] Ошибка: {e}")

def insert_highlight(user_id: int, product_id: int):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                'INSERT OR IGNORE INTO likes (user_id, product_id) VALUES (?, ?)',
                (user_id, product_id)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"[insert_highlight] Ошибка: {e}")

def delete_highlight(user_id: int, product_id: int):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                'DELETE FROM likes WHERE user_id = ? AND product_id = ?',
                (user_id, product_id)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"[delete_highlight] Ошибка: {e}")

def delete_cart(user_id: int, product_id: int, size: str = None):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            if size is not None:
                cur.execute(
                    'DELETE FROM cart WHERE user_id = ? AND product_id = ? AND size = ?',
                    (user_id, product_id, size)
                )
            else:
                cur.execute(
                    'DELETE FROM cart WHERE user_id = ? AND product_id = ? AND size IS NULL',
                    (user_id, product_id)
                )
            conn.commit()
    except sqlite3.Error as e:
        print(f"[delete_cart] Ошибка: {e}")

def insert_users(us_id: int, username: str):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                'INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)',
                (us_id, username)
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"[insert_users] Ошибка: {e}")

def insert_cart(us_id: int, product_id: int):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                'SELECT quantity FROM cart WHERE user_id = ? AND product_id = ? AND size IS NULL',
                (us_id, product_id)
            )
            existing = cur.fetchone()
            if existing:
                new_quantity = existing[0] + 1
                cur.execute(
                    'UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ? AND size IS NULL',
                    (new_quantity, us_id, product_id)
                )
            else:
                cur.execute(
                    'INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)',
                    (us_id, product_id)
                )
            conn.commit()
    except sqlite3.Error as e:
        print(f"[insert_cart] Ошибка: {e}")

def insert_cart_with_size(us_id: int, product_id: int, size: str):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                'SELECT quantity FROM cart WHERE user_id = ? AND product_id = ? AND size = ?',
                (us_id, product_id, size)
            )
            existing = cur.fetchone()
            if existing:
                new_quantity = existing[0] + 1
                cur.execute(
                    'UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ? AND size = ?',
                    (new_quantity, us_id, product_id, size)
                )
            else:
                cur.execute(
                    'INSERT INTO cart (user_id, product_id, size, quantity) VALUES (?, ?, ?, 1)',
                    (us_id, product_id, size)
                )
            conn.commit()
    except sqlite3.Error as e:
        print(f"[insert_cart_with_size] Ошибка: {e}")

def check_username_exists(username):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                'SELECT 1 FROM users WHERE username = ?',
                (username,)
            )
            return cur.fetchone() is not None
    except sqlite3.Error as e:
        print(f"[check_username_exists] Ошибка: {e}")
        return False

def check_record_exists(user_id: int, product_id: int) -> bool:
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                'SELECT EXISTS(SELECT 1 FROM likes WHERE user_id = ? AND product_id = ?)',
                (user_id, product_id)
            )
            return cur.fetchone()[0] == 1
    except sqlite3.Error as e:
        print(f"[check_record_exists] Ошибка: {e}")
        return False

def likes_database(user_id: int):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT product_id FROM likes WHERE user_id = ?", (user_id,))
            return [row[0] for row in cur.fetchall()]
    except sqlite3.Error as e:
        print(f"[likes_database] Ошибка: {e}")
        return []

def cart_database(user_id: int):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT product_id, size, quantity FROM cart WHERE user_id = ?", (user_id,))
            return cur.fetchall()
    except sqlite3.Error as e:
        print(f"[cart_database] Ошибка: {e}")
        return []

def get_categories():
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM categories")
            return [Category(id=row[0], name=row[1]) for row in cur.fetchall()]
    except sqlite3.Error as e:
        print(f"[get_categories] Ошибка: {e}")
        return []

def get_shops():
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM shops")
            return [
                Shop(
                    id=row[0],
                    name=row[1],
                    description=row[2].replace("\\n", "\n"),
                    images=row[3].split(' ') if row[3] else [],
                    status=row[4] == "True"
                ) for row in cur.fetchall()
            ]
    except sqlite3.Error as e:
        print(f"[get_shops] Ошибка: {e}")
        return []

def get_products():
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM products")
            products_data = cur.fetchall()
            products = []
            for product in products_data:
                d = product[4].replace("\\n", "\n")
                descr = '*' + product[1] + '*\n\n' + '*Цена:* ' + str(product[5]) + ' ₽\n\n' + d
                if product[7] == "True":
                    st = True
                else:
                    st = False
                p = Product(
                    id=product[0],
                    name=product[1],
                    category=product[3],
                    description=descr,
                    price=product[5],
                    images=product[6].split(' ') if product[6] else [],
                    status=st,
                    shop_id=product[2],
                    sizes=product[8].split(' ') if product[8] else []
                )
                products.append(p)
            return products
    except sqlite3.Error as e:
        print(f"[get_products] Ошибка: {e}")
        return []

def personal_data(user_id):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                    SELECT username, phone_number, [index], fio, city, street, house_number, flat_number, region 
                    FROM users WHERE id = ?
                """, (user_id,))
            return cur.fetchone()
    except sqlite3.Error as e:
        print(f"[personal_data] Ошибка: {e}")
        return None

def update_order_status(order_id, new_status=0):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                'UPDATE orders SET status = ? WHERE id = ?',
                (new_status, order_id)
            )
            conn.commit()
            return f"Статус заказа {order_id} успешно изменен"
    except Exception as e:
        print(f"Error updating order status: {e}")
        return "Ошибка при изменении статуса заказа"

def get_all_orders(message):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT o.id, o.user_id, o.shop_id, o.product_id, o.date, 
                       o.quantity, o.size, o.price, o.status,
                       u.username, s.name as shop_name, p.name as product_name
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                LEFT JOIN shops s ON o.shop_id = s.id
                LEFT JOIN products p ON o.product_id = p.id
            """)
            orders_data = cur.fetchall()
            orders = []
            for order in orders_data:
                if order[8] == 1:
                    order_str = (
                        f"🆔 ID заказа: {order[0]}\n"
                        f"👤 Пользователь: {order[9]} (ID: {order[1]})\n"
                        f"🏪 Магазин: {order[10]} (ID: {order[2]})\n"
                        f"🛍️ Товар: {order[11]} (ID: {order[3]})\n"
                        f"📅 Дата: {order[4]}\n"
                        f"🔢 Количество: {order[5]}\n"
                        f"📏 Размер: {order[6]}\n"
                        f"💰 Цена: {order[7]} руб.\n"
                        f"🔄 Статус: {order[8]}\n"
                        "────────────────────"
                    )
                    orders.append(order_str)
            return orders
    except Exception as e:
        print(f"Ошибка при получении заказов: {e}")
        return []

def get_user_info(message):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            user_id = message.text
            if not user_id.isdigit():
                bot.send_message(message.chat.id, "ID пользователя должен быть числом!")
                return
            cur.execute("""
                SELECT id, username, phone_number, [index], fio, 
                       city, street, house_number, flat_number, region
                FROM users WHERE id = ?
            """, (user_id,))
            user = cur.fetchone()
            if not user:
                bot.send_message(message.chat.id, "Пользователь не найден")
                return
            user_id = user[0]
            username = user[1] or "Не указан"
            phone = user[2] or "Не указан"
            fio = user[4] or "Не указано"
            region = user[9] or "Не указан"
            city = user[5] or "Не указан"
            street = user[6] or "Не указана"
            house = user[7] or "Не указан"
            flat = user[8] or ""
            index_code = user[3] or ""

            address_parts = [
                f"Регион: {region}",
                f"Город: {city}",
                f"Улица: {street}",
                f"Дом: {house}" + (f", Квартира: {flat}" if flat else ""),
                f"Индекс: {index_code}" if index_code else ""
            ]
            address = "\n".join(filter(None, address_parts))

            user_str = (
                f"🆔 ID: {user_id}\n"
                f"👤 Пользователь: @{username}\n"
                f"👤 ФИО: {fio}\n"
                f"📞 Телефон: {phone}\n"
                f"🏠 Адрес: \n{address}\n"
                "────────────────────"
            )

            bot.send_message(message.chat.id, user_str)

    except Exception as e:
        error_msg = f"Ошибка при получении информации о пользователе: {str(e)}"
        print(error_msg)
        bot.send_message(message.chat.id, "Произошла ошибка при обработке запроса")

def delete_user_info(message):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            user_id = message.text

            if not user_id.isdigit():
                bot.send_message(message.chat.id, "ID пользователя должен быть числом!")
                return
            cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not cur.fetchone():
                bot.send_message(message.chat.id, "Пользователь не найден")
                return
            # Удаляем пользователя
            cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            # Проверяем, что запись действительно удалилась
            cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not cur.fetchone():
                bot.send_message(message.chat.id, f"Пользователь с ID {user_id} успешно удален!")
            else:
                bot.send_message(message.chat.id, "Не удалось удалить пользователя")

    except Exception as e:
        error_msg = f"Ошибка при удалении пользователя: {str(e)}"
        print(error_msg)
        bot.send_message(message.chat.id, "Произошла ошибка при обработке запроса")

def get_all_users(message):
    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, username, phone_number, [index], fio, 
                       city, street, house_number, flat_number, region
                FROM users
            """)
            users_data = cur.fetchall()
            users = []
            for user in users_data:
                user_id = user[0]
                username = user[1] or "Не указан"
                phone = user[2] or "Не указан"
                fio = user[4] or "Не указано"
                region = user[9] or "Не указан"
                city = user[5] or "Не указан"
                street = user[6] or "Не указана"
                house = user[7] or "Не указан"
                flat = user[8] or ""
                index_code = user[3] or ""

                address_parts = [
                    f"Регион: {region}",
                    f"Город: {city}",
                    f"Улица: {street}",
                    f"Дом: {house}" + (f", Квартира: {flat}" if flat else ""),
                    f"Индекс: {index_code}" if index_code else ""
                ]
                address = ", ".join(filter(None, address_parts))
                user_str = (
                    f"🆔 ID: {user_id}\n"
                    f"👤 Пользователь: @{username}\n"
                    f"👤 ФИО: {fio}\n"
                    f"📞 Телефон: {phone}\n"
                    f"🏠 Адрес: {address}\n"
                    "────────────────────"
                )
                users.append(user_str)
            return users
    except Exception as e:
        print(f"Ошибка при получении юзеров: {e}")
        return []


def update_item_field(message, item_id, field_name):
    try:
        new_value = message.text
        if field_name in ['shop_id', 'category_id', 'price']:
            new_value = int(new_value)
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE products SET {field_name} = ? WHERE id = ?",
                        (new_value, item_id))
            conn.commit()

        bot.send_message(message.chat.id, f"Поле {field_name} товара ID {item_id} успешно обновлено!")

    except ValueError:
        bot.send_message(message.chat.id, "Ошибка: для этого поля нужно ввести число")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при обновлении: {str(e)}")
        print(f"Error updating item field: {e}")


def process_edit_cat(message, cat_id):
    try:
        new_name = message.text.strip()
        if not new_name:
            bot.send_message(message.chat.id, "Название не может быть пустым!")
            return
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM categories WHERE id = ?", (cat_id,))
            if not cur.fetchone():
                bot.send_message(message.chat.id, "Категория с таким ID не найдена!")
                return
            cur.execute("UPDATE categories SET name = ? WHERE id = ?",
                        (new_name, cat_id))
            conn.commit()

        bot.send_message(message.chat.id, f"Название категории успешно изменено!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при обновлении: {str(e)}")
        print(f"Error updating category: {e}")

def update_shop_field(message, item_id, field_name):
    try:
        new_value = message.text
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(f"UPDATE shops SET {field_name} = ? WHERE id = ?",
                        (new_value, item_id))
            conn.commit()

        bot.send_message(message.chat.id, f"Поле {field_name} магазина ID {item_id} успешно обновлено!")

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при обновлении: {str(e)}")
        print(f"Error updating shop field: {e}")

def process_item_image(message, temp_items):
    try:
        chat_id = message.chat.id
        item_data = temp_items.get(chat_id)
        if not item_data:
            raise Exception("Данные о товаре не найдены")
        item_data['images'] = message.text
        with get_db() as conn:
            cur = conn.cursor()
            if item_data['sizes'] != "-":
                size = item_data['sizes']
            else:
                size = None
            cur.execute("""
                INSERT INTO products 
                (name, shop_id, category_id, description, price, images, status, sizes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item_data['name'],
                item_data['shop_id'],
                item_data['category_id'],
                item_data['description'],
                item_data['price'],
                item_data['images'],
                item_data['status'],
                size
            ))
            conn.commit()

        new_item_id = cur.lastrowid
        bot.send_message(chat_id, f"✅ Товар успешно добавлен! ID: {new_item_id}")
        if chat_id in temp_items:
            del temp_items[chat_id]

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при сохранении товара: {str(e)}")
        print(f"Error in process_item_image: {e}")

def process_shop_status(message, temp_items):
    try:
        chat_id = message.chat.id
        item_data = temp_items.get(chat_id)

        if not item_data:
            raise Exception("Данные о магазине не найдены")
        item_data['status'] = message.text
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO shops 
                (name, description, images, status)
                VALUES (?, ?, ?, ?)
            """, (
                item_data['name'],
                item_data['description'],
                item_data['images'],
                item_data['status']
            ))
            conn.commit()
        new_item_id = cur.lastrowid
        bot.send_message(chat_id, f"✅ Магазин успешно добавлен! ID: {new_item_id}")
        if chat_id in temp_items:
            del temp_items[chat_id]
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при сохранении товара: {str(e)}")
        print(f"Error in process_item_image: {e}")