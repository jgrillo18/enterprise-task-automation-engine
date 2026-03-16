TASK_REGISTRY = {}


def register_task(name, func):
    TASK_REGISTRY[name] = func


def get_task(name):
    return TASK_REGISTRY.get(name)


def register_tasks():
    from tasks.report_task import run_report
    from tasks.sync_task import run_sync
    from tasks.backup_task import run_backup
    from tasks.cleanup_task import run_cleanup
    from tasks.health_check_task import run_health_check

    register_task("report_task", run_report)
    register_task("sync_task", run_sync)
    register_task("backup_task", run_backup)
    register_task("cleanup_task", run_cleanup)
    register_task("health_check_task", run_health_check)
