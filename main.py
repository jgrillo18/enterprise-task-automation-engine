import logging
import os
import sys
from engine.scheduler import start_scheduler
from engine.task_registry import register_tasks
from engine.dashboard import start_dashboard

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# On Render the filesystem is ephemeral — always log to stdout.
# Locally, also write to file.
handlers = [logging.StreamHandler(sys.stdout)]
if not os.environ.get("RENDER"):
    handlers.append(logging.FileHandler(os.path.join(LOG_DIR, "engine.log")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=handlers,
)

if __name__ == "__main__":
    logging.info("=" * 60)
    logging.info("Enterprise Task Automation Engine starting...")
    logging.info("=" * 60)

    start_dashboard()   # starts Flask UI on http://localhost:8080
    register_tasks()
    start_scheduler()
