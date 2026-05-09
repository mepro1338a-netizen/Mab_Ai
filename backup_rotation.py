import os

BACKUP_DIR = "/data/backups"
MAX_BACKUPS = 20

files = sorted(
    [f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")]
)

if len(files) > MAX_BACKUPS:
    files_to_delete = files[:-MAX_BACKUPS]

    for file in files_to_delete:
        path = os.path.join(BACKUP_DIR, file)

        os.remove(path)

        print(f"Gelöscht: {file}")

else:
    print("Keine alten Backups zu löschen.")
