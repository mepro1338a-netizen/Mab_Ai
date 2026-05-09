from db_manager import db

result = db.execute(
    "SELECT name FROM sqlite_master",
    fetchall=True
)

print(result)
