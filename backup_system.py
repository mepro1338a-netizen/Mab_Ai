import shutil
import os
from datetime import datetime
from config import DB_PATH

BACKUP_DIR = "/data/backups"

os.makedirs(BACKUP_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"{BACKUP_DIR}/backup_{timestamp}.db"

shutil.copy2(DB_PATH, backup_file)

print(f"Backup erstellt: {backup_file}")

