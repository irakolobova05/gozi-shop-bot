import sqlite3

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