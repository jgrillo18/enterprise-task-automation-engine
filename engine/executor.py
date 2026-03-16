import logging
from engine.task_registry import get_task
from engine.store import record_execution


def execute_task(task_name):
    task = get_task(task_name)

    if not task:
        logging.error(f"Task '{task_name}' not found in registry")
        return

    try:
        logging.info(f"Executing task: {task_name}")
        task()
        logging.info(f"Task completed successfully: {task_name}")
        record_execution(task_name, "success")
    except Exception as e:
        logging.error(f"Task '{task_name}' failed with error: {str(e)}", exc_info=True)
        record_execution(task_name, "failed", str(e))
