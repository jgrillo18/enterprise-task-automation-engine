import logging
import os
import shutil

SOURCE_DIR = os.path.join("data", "source")
DEST_DIR = os.path.join("data", "synced")


def _seed_source():
    """Create sample files the first time if source is empty."""
    os.makedirs(SOURCE_DIR, exist_ok=True)
    if not os.listdir(SOURCE_DIR):
        for i in range(1, 4):
            path = os.path.join(SOURCE_DIR, f"record_{i:03d}.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"Enterprise record #{i}\n")
        logging.info(f"Source seeded with 3 sample files in '{SOURCE_DIR}'")


def run_sync():
    logging.info("Sync task started")

    _seed_source()
    os.makedirs(DEST_DIR, exist_ok=True)

    copied = 0
    skipped = 0

    for filename in os.listdir(SOURCE_DIR):
        src = os.path.join(SOURCE_DIR, filename)
        dst = os.path.join(DEST_DIR, filename)

        if not os.path.isfile(src):
            continue

        src_mtime = os.path.getmtime(src)
        dst_mtime = os.path.getmtime(dst) if os.path.exists(dst) else 0

        if src_mtime > dst_mtime:
            shutil.copy2(src, dst)
            copied += 1
        else:
            skipped += 1

    logging.info(f"Sync complete: {copied} file(s) copied, {skipped} already up-to-date")
