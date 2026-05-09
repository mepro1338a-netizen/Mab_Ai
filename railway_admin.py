import sqlite3

conn = sqlite3.connect("/data/mabai.db")
cur = conn.cursor()

cur.execute("""
UPDATE users
SET role='admin',
    admin_level=999,
    plan='elite',
    tokens=999999
WHERE username='mepro1337'
""")

conn.commit()

user = cur.execute("""
SELECT username, role, admin_level, plan, tokens
FROM users
WHERE username='mepro1337'
""").fetchone()

print(user)

conn.close()
