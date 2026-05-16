from config import DB_PATH
import sqlite3
import os

print("DB_PATH:", DB_PATH)
print("DB_EXISTS:", os.path.exists(DB_PATH))

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("\nTABLES:")
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print("-", row["name"])

print("\nUSERS:")
try:
    users = cur.execute("SELECT username, email, plan, tokens, role, admin_level FROM users").fetchall()
    for u in users:
        print(dict(u))
except Exception as e:
    print("USERS ERROR:", e)

print("\nREDEEM CODES:")
try:
    codes = cur.execute("SELECT * FROM redeem_codes").fetchall()
    for c in codes:
        print(dict(c))
except Exception as e:
    print("CODES ERROR:", e)

conn.close()

