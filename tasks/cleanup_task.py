import datetime
import logging
import os

LOGS_DIR = "logs"
MAX_AGE_DAYS = 7  # delete log files older than this


def run_cleanup():
    logging.info(f"Cleanup task started — scanning '{LOGS_DIR}' for files older than {MAX_AGE_DAYS} days")

    now = datetime.datetime.now()
    removed = 0
    kept = 0

    for root, _, files in os.walk(LOGS_DIR):
        for filename in files:
            # Never delete the gitkeep or the active engine log
            if filename in (".gitkeep", "engine.log"):
                continue

            full_path = os.path.join(root, filename)
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(full_path))
            age_days = (now - mtime).days

            if age_days >= MAX_AGE_DAYS:
                os.remove(full_path)
                logging.info(f"Deleted old file: {full_path} (age: {age_days}d)")
                removed += 1
            else:
                kept += 1

    logging.info(f"Cleanup complete: {removed} file(s) deleted, {kept} file(s) kept")
