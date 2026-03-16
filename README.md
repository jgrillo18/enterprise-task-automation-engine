# Enterprise Task Automation Engine

A lightweight, production-ready task automation engine for recurring enterprise processes.
Inspired by Apache Airflow but focused on simplicity, low overhead, and fast deployment.

---

## Features

- **APScheduler-based** — battle-tested interval scheduling
- **YAML configuration** — add or modify tasks without touching Python code
- **Dynamic task registry** — plug in new tasks with minimal boilerplate
- **Structured logging** — logs to both `stdout` (Docker-friendly) and `logs/engine.log`
- **Robust error handling** — failed tasks are isolated and logged without crashing the engine
- **Docker ready** — runs as a non-root user inside a slim container

---

## Project Structure

```
enterprise-task-automation-engine/
│
├── engine/
│   ├── __init__.py
│   ├── scheduler.py       # APScheduler setup and task loading
│   ├── executor.py        # Task runner with error isolation
│   └── task_registry.py   # Central registry of available tasks
│
├── tasks/
│   ├── __init__.py
│   ├── report_task.py     # Report generation task
│   └── sync_task.py       # System synchronization task
│
├── config/
│   └── tasks.yaml         # Schedule configuration
│
├── logs/                  # Auto-created at runtime
│
├── main.py                # Entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Quickstart

### Run with Docker Compose (recommended)

```bash
docker compose up --build
```

Logs are persisted in `./logs/` on your host machine.

### Run with Docker directly

```bash
docker build -t enterprise-task-engine .
docker run --rm enterprise-task-engine
```

### Run locally

```bash
pip install -r requirements.txt
python main.py
```

---

## Configuration

Edit `config/tasks.yaml` to control which tasks run and how often:

```yaml
tasks:
  - name: report_task
    interval_seconds: 60

  - name: sync_task
    interval_seconds: 120
```

> No rebuild required when using Docker Compose — the `config/` volume is mounted at runtime.

---

## Adding a New Task

1. Create a new file in `tasks/`, e.g. `tasks/backup_task.py`:

```python
import logging

def run_backup():
    logging.info("Starting backup...")
    # your logic here
    logging.info("Backup completed")
```

2. Register it in `engine/task_registry.py`:

```python
from tasks.backup_task import run_backup
register_task("backup_task", run_backup)
```

3. Add it to `config/tasks.yaml`:

```yaml
- name: backup_task
  interval_seconds: 300
```

---

## Use Cases

| Use Case | Task Example |
|---|---|
| Automated reporting | `report_task` |
| System synchronization | `sync_task` |
| Database backups | `backup_task` |
| API integrations | `integration_task` |
| Data cleanup / maintenance | `cleanup_task` |

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| Scheduler | APScheduler 3.x |
| Config | YAML |
| Logging | Python `logging` (structured) |
| Containerization | Docker / Docker Compose |

---

## What This Demonstrates

This project shows the ability to build:

- **Automation engines** — lightweight alternatives to heavy orchestration tools
- **Extensible systems** — plug-and-play task architecture
- **Enterprise-grade tooling** — structured logging, error isolation, container-ready deployment
- **Platform / DevOps engineering** — scheduling, process automation, infrastructure tooling

Highly relevant for roles in:
- Automation Engineering
- Platform Engineering
- DevOps / SRE
- Enterprise Software Development
- Telecommunications / Operations
