import datetime
import logging
import os
import zipfile

LOGS_DIR = "logs"
BACKUPS_DIR = "backups"
MAX_BACKUPS = 10  # keep only the latest N zip files


def run_backup():
    logging.info("Backup task started")

    os.makedirs(BACKUPS_DIR, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(BACKUPS_DIR, f"logs_backup_{timestamp}.zip")

    files_added = 0
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(LOGS_DIR):
            for filename in files:
                if filename == ".gitkeep":
                    continue
                full_path = os.path.join(root, filename)
                arcname = os.path.relpath(full_path, start=".")
                zf.write(full_path, arcname)
                files_added += 1

    if files_added == 0:
        os.remove(zip_path)
        logging.info("Backup skipped — no log files to archive yet")
        return

    size_kb = os.path.getsize(zip_path) / 1024
    logging.info(f"Backup created -> {zip_path} ({files_added} file(s), {size_kb:.1f} KB)")

    # Rotate: remove oldest backups beyond MAX_BACKUPS
    backups = sorted(
        [f for f in os.listdir(BACKUPS_DIR) if f.endswith(".zip")],
    )
    for old in backups[:-MAX_BACKUPS]:
        os.remove(os.path.join(BACKUPS_DIR, old))
        logging.info(f"Old backup removed: {old}")
