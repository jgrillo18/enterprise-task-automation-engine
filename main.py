import logging
import os
import sys
from engine.scheduler import start_scheduler
from engine.task_registry import register_tasks
from engine.dashboard import start_dashboard

LOG_DIR = "logs"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Log to both file and stdout so Docker logs work correctly
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "engine.log")),
        logging.StreamHandler(sys.stdout),
    ],
)

if __name__ == "__main__":
    logging.info("=" * 60)
    logging.info("Enterprise Task Automation Engine starting...")
    logging.info("=" * 60)

    start_dashboard()   # starts Flask UI on http://localhost:8080
    register_tasks()
    start_scheduler()
