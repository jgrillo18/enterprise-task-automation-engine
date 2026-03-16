import csv
import datetime
import logging
import os

REPORTS_DIR = os.path.join("logs", "reports")


def run_report():
    logging.info("Report task started")

    os.makedirs(REPORTS_DIR, exist_ok=True)

    from engine.store import task_stats

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(REPORTS_DIR, f"report_{timestamp}.csv")

    rows = []
    for name, stats in task_stats.items():
        rows.append({
            "task_name": name,
            "run_count": stats.get("run_count", 0),
            "success_count": stats.get("success_count", 0),
            "fail_count": stats.get("fail_count", 0),
            "last_run": stats.get("last_run", "-"),
            "last_status": stats.get("last_status", "-"),
        })

    if not rows:
        logging.info("No task stats yet — report skipped")
        return

    fieldnames = ["task_name", "run_count", "success_count", "fail_count", "last_run", "last_status"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logging.info(f"Report saved -> {filename} ({len(rows)} task(s) recorded)")
