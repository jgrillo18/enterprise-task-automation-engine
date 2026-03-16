import logging
import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from engine.executor import execute_task

scheduler = BlockingScheduler()

CONFIG_FILE = "config/tasks.yaml"


def job_listener(event):
    if event.exception:
        logging.error(f"Job {event.job_id} raised an exception")
    else:
        logging.info(f"Job {event.job_id} executed successfully")


def load_tasks():
    with open(CONFIG_FILE, "r") as f:
        config = yaml.safe_load(f)
    return config.get("tasks", [])


def start_scheduler():
    tasks = load_tasks()

    if not tasks:
        logging.warning("No tasks found in configuration file")
        return

    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    for task in tasks:
        name = task["name"]
        interval = task["interval_seconds"]

        scheduler.add_job(
            execute_task,
            "interval",
            seconds=interval,
            args=[name],
            id=name,
        )

        logging.info(f"Scheduled task '{name}' every {interval} seconds")

    logging.info(f"Scheduler started with {len(tasks)} task(s)")
    logging.info("Press Ctrl+C to stop")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
        logging.info("Scheduler stopped")
