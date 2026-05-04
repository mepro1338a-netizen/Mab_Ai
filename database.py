import sqlite3, time, uuid, hashlib, secrets, string
from config import DB_PATH, PLANS

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 180000).hex()

def init_db():
    conn = get_conn(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, email TEXT UNIQUE, password_hash TEXT NOT NULL, salt TEXT NOT NULL,
        plan TEXT DEFAULT 'free', tokens INTEGER DEFAULT 5, role TEXT DEFAULT 'user',
        created_at REAL, last_login REAL, images_used INTEGER DEFAULT 0, videos_used INTEGER DEFAULT 0,
        content_used INTEGER DEFAULT 0, music_used INTEGER DEFAULT 0,
        email_verified INTEGER DEFAULT 0, verification_code TEXT, last_seen REAL DEFAULT 0,
        last_ip TEXT DEFAULT '')""")
    for sql in [
        "ALTER TABLE users ADD COLUMN music_used INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN verification_code TEXT",
        "ALTER TABLE users ADD COLUMN last_seen REAL DEFAULT 0",
        "ALTER TABLE users ADD COLUMN last_ip TEXT DEFAULT ''"
    ]:
        try:
            c.execute(sql)
        except sqlite3.OperationalError:
            pass
    c.execute("""CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, plan TEXT, stripe_session_id TEXT, status TEXT, created_at REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, memory_key TEXT, memory_value TEXT, created_at REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS redeem_codes (
        code TEXT PRIMARY KEY, code_type TEXT, value TEXT, tokens INTEGER DEFAULT 0, plan TEXT,
        max_uses INTEGER DEFAULT 1, used_count INTEGER DEFAULT 0, created_by TEXT, created_at REAL,
        expires_at REAL, active INTEGER DEFAULT 1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS code_redemptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, username TEXT, redeemed_at REAL)""")
    salt = uuid.uuid4().hex; pw = hash_password("admin", salt)
    c.execute("""INSERT OR IGNORE INTO users
        (username,email,password_hash,salt,plan,tokens,role,created_at,last_login)
        VALUES (?,?,?,?,?,?,?,?,?)""", ("admin","admin@mab.ai",pw,salt,"elite",10000,"admin",time.time(),time.time()))
    c.execute("UPDATE users SET email_verified=1 WHERE username='admin'")
    conn.commit(); conn.close()

def create_user(username, email, password, role="user", plan="free", tokens=None):
    username=(username or "").strip().lower(); email=(email or "").strip().lower()
    role = role if role in ("user","moderator","admin") else "user"; plan = plan if plan in PLANS else "free"
    tokens = 0 if tokens is None else int(tokens)
    if len(username)<3: return False, "Username must be at least 3 characters."
    if "@" not in email or "." not in email: return False, "Please enter a valid email."
    if len(password or "")<6: return False, "Password must be at least 6 characters."
    conn=get_conn(); c=conn.cursor()
    if c.execute("SELECT username FROM users WHERE username=? OR email=?", (username,email)).fetchone():
        conn.close(); return False, "Username or email already exists."

    c.execute("""
    CREATE TABLE IF NOT EXISTS support_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        category TEXT,
        subject TEXT,
        message TEXT,
        status TEXT DEFAULT 'open',
        is_read INTEGER DEFAULT 0,
        created_at REAL,
        updated_at REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS admin_chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        role TEXT,
        message TEXT,
        created_at REAL
    )
    """)

    salt=uuid.uuid4().hex; pw=hash_password(password, salt)
    verification_code = generate_code(prefix="VERIFY", length=8)
    c.execute("""INSERT INTO users (username,email,password_hash,salt,plan,tokens,role,created_at,last_login,email_verified,verification_code)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (username,email,pw,salt,plan,tokens,role,time.time(),0,0,verification_code))
    conn.commit(); conn.close()
    return True, f"Account created. Verify your email to receive your free tokens. Verification code: {verification_code}"

def verify_user(username, password):
    username=(username or "").strip().lower(); conn=get_conn(); c=conn.cursor()
    row=c.execute("""SELECT username,email,password_hash,salt,plan,tokens,role,images_used,videos_used,content_used,music_used,email_verified,last_ip,last_seen
        FROM users WHERE username=?""", (username,)).fetchone()
    if not row: conn.close(); return False, "User not found.", None
    db_user,email,pwh,salt,plan,tokens,role,iu,vu,cu,mu,email_verified,last_ip,last_seen=row
    if hash_password(password or "", salt) != pwh: conn.close(); return False, "Wrong password.", None
    c.execute("UPDATE users SET last_login=? WHERE username=?", (time.time(), username)); conn.commit(); conn.close()
    return True, "Login successful.", {"username":db_user,"email":email,"plan":plan,"tokens":tokens,"role":role,"images_used":iu,"videos_used":vu,"content_used":cu,"music_used":mu,"email_verified":email_verified,"last_ip":last_ip,"last_seen":last_seen}

def get_user(username):
    if not username: return None
    conn=get_conn(); c=conn.cursor()
    row=c.execute("""SELECT username,email,plan,tokens,role,images_used,videos_used,content_used,music_used,email_verified,last_ip,last_seen FROM users WHERE username=?""", (username,)).fetchone()
    conn.close()
    if not row: return None
    return {"username":row[0],"email":row[1],"plan":row[2],"tokens":row[3],"role":row[4],"images_used":row[5],"videos_used":row[6],"content_used":row[7],"music_used":row[8],"email_verified":row[9],"last_ip":row[10],"last_seen":row[11]}

def update_tokens(username, amount):
    conn=get_conn(); c=conn.cursor(); c.execute("UPDATE users SET tokens=MAX(tokens+?,0) WHERE username=?", (int(amount),username)); conn.commit(); conn.close()

def set_plan(username, plan, add_tokens=True):
    if plan not in PLANS: return False
    conn=get_conn(); c=conn.cursor()
    if add_tokens: c.execute("UPDATE users SET plan=?, tokens=tokens+? WHERE username=?", (plan,PLANS[plan]["tokens"],username))
    else: c.execute("UPDATE users SET plan=? WHERE username=?", (plan,username))
    conn.commit(); conn.close(); return True

def set_role(username, role):
    if role not in ("user","moderator","admin"): return False
    conn=get_conn(); c=conn.cursor(); c.execute("UPDATE users SET role=? WHERE username=?", (role,username)); conn.commit(); conn.close(); return True

def delete_user(username):
    if username == "admin": return False
    conn=get_conn(); c=conn.cursor(); c.execute("DELETE FROM users WHERE username=?", (username,)); c.execute("DELETE FROM memory WHERE username=?", (username,)); conn.commit(); conn.close(); return True

def increment_usage(username, field):
    if field not in {"images_used","videos_used","content_used","music_used"}: return
    conn=get_conn(); c=conn.cursor(); c.execute(f"UPDATE users SET {field}={field}+1 WHERE username=?", (username,)); conn.commit(); conn.close()

def add_purchase(username, plan, stripe_session_id="manual", status="paid"):
    conn=get_conn(); c=conn.cursor(); c.execute("INSERT INTO purchases (username,plan,stripe_session_id,status,created_at) VALUES (?,?,?,?,?)", (username,plan,stripe_session_id,status,time.time())); conn.commit(); conn.close()

def list_purchases(username=None):
    conn=get_conn(); c=conn.cursor()
    if username: rows=c.execute("SELECT username,plan,stripe_session_id,status,created_at FROM purchases WHERE username=? ORDER BY created_at DESC", (username,)).fetchall()
    else: rows=c.execute("SELECT username,plan,stripe_session_id,status,created_at FROM purchases ORDER BY created_at DESC").fetchall()
    conn.close(); return rows

def list_users():
    conn=get_conn(); c=conn.cursor()
    rows=c.execute("SELECT username,email,plan,tokens,role,images_used,videos_used,content_used,music_used,email_verified,last_ip,last_seen,created_at FROM users ORDER BY created_at DESC").fetchall()
    conn.close(); return rows

def add_memory(username, key, value):
    if not key or not value: return
    conn=get_conn(); c=conn.cursor(); c.execute("INSERT INTO memory (username,memory_key,memory_value,created_at) VALUES (?,?,?,?)", (username,key,value,time.time())); conn.commit(); conn.close()

def load_memory(username, limit=10):
    conn=get_conn(); c=conn.cursor(); rows=c.execute("SELECT memory_key,memory_value FROM memory WHERE username=? ORDER BY created_at DESC LIMIT ?", (username,limit)).fetchall(); conn.close(); return rows

def generate_code(prefix="MAB", length=10):
    return prefix + "-" + "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def create_redeem_code(code_type, value, tokens, plan, max_uses, created_by, days_valid=30):
    code=generate_code(); expires_at=time.time()+int(days_valid)*86400 if days_valid else None
    conn=get_conn(); c=conn.cursor()
    c.execute("""INSERT INTO redeem_codes (code,code_type,value,tokens,plan,max_uses,used_count,created_by,created_at,expires_at,active)
        VALUES (?,?,?,?,?,?,0,?,?,?,1)""", (code,code_type,value,int(tokens or 0),plan,int(max_uses or 1),created_by,time.time(),expires_at))
    conn.commit(); conn.close(); return code

def list_codes():
    conn=get_conn(); c=conn.cursor(); rows=c.execute("SELECT code,code_type,value,tokens,plan,max_uses,used_count,created_by,created_at,expires_at,active FROM redeem_codes ORDER BY created_at DESC").fetchall(); conn.close(); return rows

def redeem_code(username, code):
    code=(code or "").strip().upper()
    if not code: return False, "Enter a code."
    conn=get_conn(); c=conn.cursor()
    row=c.execute("SELECT code,code_type,value,tokens,plan,max_uses,used_count,expires_at,active FROM redeem_codes WHERE code=?", (code,)).fetchone()
    if not row: conn.close(); return False, "Code not found."
    code,code_type,value,tokens,plan,max_uses,used_count,expires_at,active=row
    if not active: conn.close(); return False, "Code is disabled."
    if expires_at and time.time()>expires_at: conn.close(); return False, "Code expired."
    if used_count>=max_uses: conn.close(); return False, "Code already used too many times."
    if c.execute("SELECT id FROM code_redemptions WHERE username=? AND code=?", (username,code)).fetchone():
        conn.close(); return False, "You already redeemed this code."
    if code_type=="tokens": c.execute("UPDATE users SET tokens=tokens+? WHERE username=?", (int(tokens),username))
    elif code_type=="plan":
        if plan not in PLANS: conn.close(); return False, "Invalid plan code."
        c.execute("UPDATE users SET plan=?, tokens=tokens+? WHERE username=?", (plan,PLANS[plan]["tokens"],username))
    c.execute("UPDATE redeem_codes SET used_count=used_count+1 WHERE code=?", (code,))
    c.execute("INSERT INTO code_redemptions (code,username,redeemed_at) VALUES (?,?,?)", (code,username,time.time()))
    conn.commit(); conn.close()
    if code_type=="tokens": return True, f"Code redeemed. Added {tokens} tokens."
    if code_type=="plan": return True, f"Code redeemed. Plan upgraded to {PLANS[plan]['label']}."
    return True, f"Discount code redeemed: {value}"


def touch_user(username, ip=""):
    if not username:
        return
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET last_seen=?, last_ip=? WHERE username=?", (time.time(), ip or "", username))
    conn.commit()
    conn.close()


def verify_email_code(username, code):
    username = (username or "").strip().lower()
    code = (code or "").strip().upper()

    conn = get_conn()
    c = conn.cursor()

    row = c.execute("SELECT email_verified, verification_code, tokens FROM users WHERE username=?", (username,)).fetchone()
    if not row:
        conn.close()
        return False, "User not found."

    email_verified, verification_code, tokens = row

    if email_verified:
        conn.close()
        return True, "Email already verified."

    if not verification_code or code != verification_code:
        conn.close()
        return False, "Wrong verification code."

    # Give free starter tokens only after verification
    c.execute("UPDATE users SET email_verified=1, verification_code=NULL, tokens=tokens+5 WHERE username=?", (username,))
    conn.commit()
    conn.close()
    return True, "Email verified. 5 free tokens added."


def get_verification_code_admin(username):
    conn = get_conn()
    c = conn.cursor()
    row = c.execute("SELECT verification_code FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row[0] if row else None


# ======================
# SUPPORT / ADMIN CHAT
# ======================

def create_support_message(username, email, category, subject, message):
    username = (username or "").strip().lower()
    email = (email or "").strip().lower()
    category = (category or "General").strip()
    subject = (subject or "").strip()
    message = (message or "").strip()

    if len(subject) < 3:
        return False, "Subject is too short."
    if len(message) < 5:
        return False, "Message is too short."

    conn = get_conn()
    c = conn.cursor()
    now = time.time()
    c.execute("""
    INSERT INTO support_messages (username, email, category, subject, message, status, is_read, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, 'open', 0, ?, ?)
    """, (username, email, category, subject, message, now, now))
    conn.commit()
    conn.close()
    return True, "Support message sent."


def list_support_messages(status_filter=None):
    conn = get_conn()
    c = conn.cursor()

    if status_filter and status_filter != "all":
        rows = c.execute("""
        SELECT id, username, email, category, subject, message, status, is_read, created_at, updated_at
        FROM support_messages
        WHERE status=?
        ORDER BY is_read ASC, created_at DESC
        """, (status_filter,)).fetchall()
    else:
        rows = c.execute("""
        SELECT id, username, email, category, subject, message, status, is_read, created_at, updated_at
        FROM support_messages
        ORDER BY is_read ASC, created_at DESC
        """).fetchall()

    conn.close()
    return rows


def support_counts():
    conn = get_conn()
    c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM support_messages").fetchone()[0]
    unread = c.execute("SELECT COUNT(*) FROM support_messages WHERE is_read=0").fetchone()[0]
    open_count = c.execute("SELECT COUNT(*) FROM support_messages WHERE status='open'").fetchone()[0]
    closed = c.execute("SELECT COUNT(*) FROM support_messages WHERE status='closed'").fetchone()[0]
    conn.close()
    return {"total": total, "unread": unread, "open": open_count, "closed": closed}


def set_support_read(message_id, is_read=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE support_messages SET is_read=?, updated_at=? WHERE id=?", (int(is_read), time.time(), int(message_id)))
    conn.commit()
    conn.close()


def set_support_status(message_id, status):
    if status not in ("open", "closed"):
        return False
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE support_messages SET status=?, updated_at=? WHERE id=?", (status, time.time(), int(message_id)))
    conn.commit()
    conn.close()
    return True


def delete_support_message(message_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM support_messages WHERE id=?", (int(message_id),))
    conn.commit()
    conn.close()


def add_admin_chat(username, role, message):
    message = (message or "").strip()
    if not message:
        return False, "Message is empty."

    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    INSERT INTO admin_chat (username, role, message, created_at)
    VALUES (?, ?, ?, ?)
    """, (username, role, message, time.time()))
    conn.commit()
    conn.close()
    return True, "Message sent."


def list_admin_chat(limit=50):
    conn = get_conn()
    c = conn.cursor()
    rows = c.execute("""
    SELECT username, role, message, created_at
    FROM admin_chat
    ORDER BY created_at DESC
    LIMIT ?
    """, (int(limit),)).fetchall()
    conn.close()
    return list(reversed(rows))
