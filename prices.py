import sqlite3

DB_PATH = 'prices.db'

def init_prices_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('''
CREATE TABLE IF NOT EXISTS prices (
    name TEXT PRIMARY KEY,
    price REAL,
    position INTEGER
    )
    ''')
        conn.commit()

def get_all_prices():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name, price FROM prices ORDER BY name ASC")
        return cur.fetchall()

def set_price(item, price, position):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO prices (name, price, position) VALUES (?, ?, ?)",
            (item.lower(), price, position)
        )

def clear_all_prices():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM prices")
        conn.commit()