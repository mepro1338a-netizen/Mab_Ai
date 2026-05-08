import sqlite3
import threading
import time
from config import DB_PATH

class DatabaseManager:
    def __init__(self):
        self.lock = threading.Lock()

    def get_connection(self):
        conn = sqlite3.connect(
            DB_PATH,
            check_same_thread=False,
            timeout=30
        )

        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")

        return conn

    def execute(self, query, params=(), fetchone=False, fetchall=False):
        retries = 3

        for attempt in range(retries):
            try:
                with self.lock:
                    conn = self.get_connection()
                    cur = conn.cursor()

                    cur.execute(query, params)

                    result = None

                    if fetchone:
                        result = cur.fetchone()

                    elif fetchall:
                        result = cur.fetchall()

                    conn.commit()
                    conn.close()

                    return result

            except sqlite3.OperationalError as e:
                print(f"DB Error: {e}")

                if attempt < retries - 1:
                    time.sleep(1)
                else:
                    raise e

db = DatabaseManager()