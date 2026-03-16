# Enterprise Task Automation Engine

[![CI](https://github.com/jgrillo18/enterprise-task-automation-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/jgrillo18/enterprise-task-automation-engine/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Deploy](https://img.shields.io/badge/live%20demo-render-46E3B7?logo=render&logoColor=white)](https://enterprise-task-automation-engine.onrender.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A lightweight, production-ready task automation engine for recurring enterprise processes.  
Inspired by Apache Airflow but focused on simplicity, low overhead, and fast deployment.

---

## Live Demo

**[https://enterprise-task-automation-engine.onrender.com](https://enterprise-task-automation-engine.onrender.com)**

> The dashboard shows real tasks executing in production — KPI cards, per-task stats, next scheduled run, and a live log console. Supports English, Spanish and Portuguese.

---

## Features

- **APScheduler-based** — battle-tested interval scheduling
- **YAML configuration** — add or modify tasks without touching Python code
- **Dynamic task registry** — plug in new tasks with minimal boilerplate
- **Web dashboard** — live KPI cards, task status, next-run times and log console
- **i18n support** — language switcher EN / ES / PT (persisted in browser)
- **Structured logging** — logs to both `stdout` (Docker-friendly) and `logs/engine.log`
- **Robust error handling** — failed tasks are isolated and logged without crashing the engine
- **Docker ready** — runs as a non-root user inside a slim container
- **Render ready** — one-click deploy via `render.yaml`

---

## Project Structure

```
enterprise-task-automation-engine/
│
├── engine/
│   ├── __init__.py
│   ├── scheduler.py       # APScheduler setup and task loading
│   ├── executor.py        # Task runner with error isolation
│   ├── task_registry.py   # Central registry of available tasks
│   ├── store.py           # Shared in-memory state for the dashboard
│   └── dashboard.py       # Flask web dashboard (runs in background thread)
│
├── tasks/
│   ├── __init__.py
│   ├── report_task.py         # Generates a CSV report with execution stats
│   ├── sync_task.py           # Syncs files from data/source/ to data/synced/
│   ├── backup_task.py         # Creates a timestamped zip of the logs/ folder
│   ├── cleanup_task.py        # Deletes log files older than 7 days
│   └── health_check_task.py   # HTTP health check for external endpoints
│
├── config/
│   └── tasks.yaml         # Schedule configuration
│
├── .github/
│   └── workflows/
│       └── ci.yml         # GitHub Actions: lint + Docker build
│
├── logs/                  # Auto-created at runtime
├── backups/               # Auto-created at runtime
├── data/
│   └── source/            # Source files for sync task
│
├── main.py                # Entry point
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── render.yaml            # Render deployment config
└── README.md
```

---

## Quickstart

### Run with Docker Compose (recommended)

```bash
docker compose up --build
```

Logs are persisted in `./logs/` and config is hot-reloaded from `./config/`.

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

Open the dashboard at **http://localhost:8080**

---

## Dashboard

The built-in web UI (Flask, Bootstrap 5, dark mode) provides:

| Section | Description |
|---|---|
| KPI cards | Tasks registered / Successful runs / Failed runs / Uptime |
| Task cards | Per-task status badge, last run, next run, total runs, failures |
| Live log console | Auto-refreshes every 3 seconds, errors in red, warnings in orange |
| Language switcher | EN / ES / PT — selection persisted in `localStorage` |

---

## Tasks Included

| Task | What it does | Default interval |
|---|---|---|
| `health_check_task` | HTTP GET to Google, GitHub and PyPI — logs status code and latency | 45 s |
| `report_task` | Writes a CSV to `logs/reports/` with execution stats for all tasks | 60 s |
| `sync_task` | Copies new/modified files from `data/source/` to `data/synced/` | 90 s |
| `backup_task` | Creates a compressed zip of `logs/` in `backups/`, rotates old ones | 180 s |
| `cleanup_task` | Deletes log and report files older than 7 days | 300 s |

---

## Configuration

Edit `config/tasks.yaml` to control which tasks run and how often:

```yaml
tasks:
  - name: report_task
    interval_seconds: 60

  - name: sync_task
    interval_seconds: 90
```

> No rebuild required when using Docker Compose — the `config/` volume is mounted at runtime.

---

## Adding a New Task

1. Create `tasks/my_task.py`:

```python
import logging

def run_my_task():
    logging.info("My task started")
    # your logic here
    logging.info("My task completed")
```

2. Register it in `engine/task_registry.py`:

```python
from tasks.my_task import run_my_task
register_task("my_task", run_my_task)
```

3. Add it to `config/tasks.yaml`:

```yaml
- name: my_task
  interval_seconds: 300
```

---

## Deploy to Render (one click)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/jgrillo18/enterprise-task-automation-engine)

Or manually:
1. Go to [render.com](https://render.com) → **New Web Service**
2. Connect `jgrillo18/enterprise-task-automation-engine`
3. Render detects `render.yaml` automatically — click **Deploy**

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| Scheduler | APScheduler 3.x |
| Web dashboard | Flask 3.x + Bootstrap 5 |
| Config | YAML |
| Logging | Python `logging` (structured) |
| Containerization | Docker / Docker Compose |
| CI/CD | GitHub Actions |
| Hosting | Render |

---

## What This Demonstrates

This project shows the ability to build:

- **Automation engines** — lightweight alternatives to heavy orchestration tools
- **Extensible systems** — plug-and-play task architecture
- **Enterprise-grade tooling** — structured logging, error isolation, container-ready deployment
- **Full-stack platform engineering** — backend scheduler + live web dashboard + CI/CD pipeline
- **Internationalization** — multi-language UI without external libraries

Highly relevant for roles in:
- Automation Engineering
- Platform Engineering
- DevOps / SRE
- Enterprise Software Development
- Telecommunications / Operations

