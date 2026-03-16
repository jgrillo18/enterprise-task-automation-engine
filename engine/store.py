"""
Shared in-memory state for the dashboard UI.
Both the executor and the dashboard read/write from here.
"""
import datetime
import threading
from collections import deque

_lock = threading.Lock()

# Ring buffer of the last 500 log lines (fed by UILogHandler in dashboard.py)
log_buffer: deque = deque(maxlen=500)

# Per-task execution statistics
task_stats: dict = {}

# Engine start time
start_time: datetime.datetime = datetime.datetime.now()


def record_execution(task_name: str, status: str, error: str = None) -> None:
    """Record the result of a task execution (called from executor.py)."""
    with _lock:
        if task_name not in task_stats:
            task_stats[task_name] = {
                "run_count": 0,
                "success_count": 0,
                "fail_count": 0,
                "last_run": None,
                "last_status": "pending",
                "last_error": None,
            }
        s = task_stats[task_name]
        s["last_run"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        s["last_status"] = status
        s["run_count"] += 1
        if status == "success":
            s["success_count"] += 1
        else:
            s["fail_count"] += 1
            s["last_error"] = error
