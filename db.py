import sqlite3
"""
# Yhdistetään tietokantaan
conn = sqlite3.connect('piikit.db')
cursor = conn.cursor()

# Luodaan taulu, jos sitä ei ole
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT,
    balance INTEGER DEFAULT 0
)
''')
conn.commit()
"""

def checkIfIDExists(userID):
  conn = sqlite3.connect('piikit.db')
  cur = conn.cursor()
  cur.execute("SELECT id FROM users WHERE id = ?", (str(userID),))
  rows = cur.fetchall()
  cur.close()
  return len(rows) == 1

def addToDb(userID, name):
  conn = sqlite3.connect('piikit.db')
  cur = conn.cursor()
  cur.execute("INSERT INTO users (id, name, balance) VALUES (?, ?, 0)", (str(userID), name))
  conn.commit()
  cur.close()
  return

def update_name(userID, new_name):
    conn = sqlite3.connect('piikit.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, str(userID)))
    conn.commit()
    cur.close()

def update_balance(user_id, amount):
    conn = sqlite3.connect('piikit.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, str(user_id)))
    conn.commit()
    cur.execute("SELECT balance FROM users WHERE id = ?", (str(user_id),))
    new_balance = cur.fetchone()[0]
    cur.close()
    return new_balance

def get_balance(user_id):
    conn = sqlite3.connect('piikit.db')
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE id = ?", (str(user_id),))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None

def get_all_users():
    conn = sqlite3.connect('piikit.db')
    cur = conn.cursor()
    cur.execute("SELECT name, balance FROM users ORDER BY balance ASC")
    rows = cur.fetchall()
    cur.close()
    return rows





"""
def get_or_create_user(name):
    cursor.execute("SELECT balance FROM users WHERE name = ?", (name))
    row = cursor.fetchone()
    if row is None:
        cursor.execute("INSERT INTO users (name, balance) VALUES (?, ?)", (name, 0))
        conn.commit()
        print(f"Uusi käyttäjä {name} luotu saldolla 0 €")
        return 0
    return row[0]

def update_balance(name, amount):
    cursor.execute("UPDATE users SET balance = balance + ? WHERE name = ?", (amount, name))
    conn.commit()
    cursor.execute("SELECT balance FROM users WHERE name = ?", (name,))
    return cursor.fetchone()[0]

def show_all_users():
    cursor.execute("SELECT name, balance FROM users")
    rows = cursor.fetchall()
    print("\nKaikki käyttäjät ja saldot:")
    for name, balance in rows:
        print(f"{name}: {balance} €")

def close_connection():
    conn.close()
"""