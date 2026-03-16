"""
Lightweight web dashboard for the task automation engine.
Runs in a background thread alongside the APScheduler.
Access at http://localhost:8080
"""
import datetime
import logging
import threading

from flask import Flask, Response, jsonify, request

from engine.store import log_buffer, start_time, task_stats

app = Flask(__name__)

# Silence Flask's default request logs so they don't pollute the engine log
logging.getLogger("werkzeug").setLevel(logging.ERROR)


# ---------------------------------------------------------------------------
# Log capture – feeds every log record into the in-memory ring buffer
# ---------------------------------------------------------------------------

class UILogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            log_buffer.append(self.format(record))
        except Exception:
            pass


def _setup_log_handler() -> None:
    handler = UILogHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    logging.getLogger().addHandler(handler)


# ---------------------------------------------------------------------------
# HTML dashboard (single-page, data fetched via JS)
# ---------------------------------------------------------------------------

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Task Automation Engine</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" />
  <style>
    body { background:#0f1117; color:#e0e0e0; font-family:"Segoe UI",sans-serif; }
    .card { background:#1a1d27; border:1px solid #2a2d3e; border-radius:10px; }
    .card-header { background:#12152a; border-bottom:1px solid #2a2d3e; font-weight:600; }
    .navbar { background:#12152a !important; border-bottom:1px solid #2a2d3e; }
    .stat-val { font-size:2.2rem; font-weight:700; }
    .dot { width:10px; height:10px; border-radius:50%; display:inline-block; margin-right:6px; }
    .dot-green { background:#28a745; animation:pulse 1.4s infinite; }
    @keyframes pulse { 0%,100%{ opacity:1 } 50%{ opacity:.3 } }
    #log-console {
      background:#080b12; color:#00e676; font-family:monospace;
      font-size:12.5px; height:380px; overflow-y:auto; padding:14px;
      border-radius:0 0 10px 10px;
    }
    #log-console .err { color:#ff5252; }
    #log-console .warn { color:#ffab40; }
    .task-name { font-size:1rem; font-weight:600; color:#fff; }
    .ts { color:#8892a4; font-size:.78rem; }
    .lang-btn { min-width:42px; font-size:.8rem; padding:3px 8px; }
    .lang-btn.active { background:#4f6ef7; border-color:#4f6ef7; color:#fff; }
  </style>
</head>
<body>
<nav class="navbar navbar-dark mb-4 px-4 d-flex justify-content-between align-items-center">
  <span class="navbar-brand fw-bold fs-5">
    <span class="dot dot-green"></span><span data-i18n="title">Enterprise Task Automation Engine</span>
  </span>
  <div class="d-flex align-items-center gap-3">
    <span class="ts" id="updated">-</span>
    <div class="btn-group" role="group" aria-label="Language">
      <button class="btn btn-outline-light lang-btn active" onclick="setLang('en')" id="btn-en">EN</button>
      <button class="btn btn-outline-light lang-btn" onclick="setLang('es')" id="btn-es">ES</button>
      <button class="btn btn-outline-light lang-btn" onclick="setLang('pt')" id="btn-pt">PT</button>
    </div>
  </div>
</nav>

<div class="container-fluid px-4">
  <div class="row g-3 mb-4" id="kpi-row"></div>
  <div class="row g-3 mb-4" id="task-row"></div>
  <div class="card mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <span>&#128196; <span data-i18n="live_logs">Live Logs</span></span>
      <button class="btn btn-sm btn-outline-secondary" onclick="clearConsole()" data-i18n="clear">Clear</button>
    </div>
    <div id="log-console"></div>
  </div>
</div>

<script>
  // ── i18n strings ──────────────────────────────────────────────────────────
  const I18N = {
    en: {
      title:          "Enterprise Task Automation Engine",
      tasks_reg:      "Tasks Registered",
      successful:     "Successful Runs",
      failed_runs:    "Failed Runs",
      uptime:         "Uptime",
      last_run:       "Last run",
      next_run:       "Next run",
      total_runs:     "Total runs",
      failures:       "Failures",
      live_logs:      "Live Logs",
      clear:          "Clear",
      updated:        "Updated",
      status: { success:"success", failed:"failed", pending:"pending" },
    },
    es: {
      title:          "Motor de Automatizacion Empresarial",
      tasks_reg:      "Tareas Registradas",
      successful:     "Ejecuciones Exitosas",
      failed_runs:    "Ejecuciones Fallidas",
      uptime:         "Tiempo Activo",
      last_run:       "Ultima ejecucion",
      next_run:       "Proxima ejecucion",
      total_runs:     "Total ejecuciones",
      failures:       "Fallos",
      live_logs:      "Logs en Vivo",
      clear:          "Limpiar",
      updated:        "Actualizado",
      status: { success:"exitoso", failed:"fallido", pending:"pendiente" },
    },
    pt: {
      title:          "Motor de Automacao Empresarial",
      tasks_reg:      "Tarefas Registradas",
      successful:     "Execucoes Bem-sucedidas",
      failed_runs:    "Execucoes com Falha",
      uptime:         "Tempo Ativo",
      last_run:       "Ultima execucao",
      next_run:       "Proxima execucao",
      total_runs:     "Total de execucoes",
      failures:       "Falhas",
      live_logs:      "Logs ao Vivo",
      clear:          "Limpar",
      updated:        "Atualizado",
      status: { success:"sucesso", failed:"falhou", pending:"pendente" },
    },
  };

  let lang = localStorage.getItem('dash_lang') || 'en';
  let seen = 0;

  function t(key) { return (I18N[lang] || I18N.en)[key] || key; }

  function setLang(l) {
    lang = l;
    localStorage.setItem('dash_lang', l);
    document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('btn-' + l).classList.add('active');
    // Re-translate static elements
    document.querySelectorAll('[data-i18n]').forEach(el => {
      el.textContent = t(el.dataset.i18n);
    });
    // Force a full data refresh to re-render cards in new language
    refresh();
  }

  function badge(status) {
    const map = { success:'success', failed:'danger', pending:'secondary' };
    const label = (t('status') || {})[status] || status;
    return `<span class="badge bg-${map[status]||'secondary'} ms-1">${label}</span>`;
  }

  function kpiCard(value, labelKey, colorClass) {
    return `<div class="col-6 col-md-3"><div class="card text-center py-3 px-2">
      <div class="stat-val ${colorClass}">${value}</div>
      <div class="ts mt-1">${t(labelKey)}</div>
    </div></div>`;
  }

  async function refresh() {
    try {
      const r = await fetch('/api/status');
      const d = await r.json();

      document.getElementById('kpi-row').innerHTML =
        kpiCard(d.total_tasks,    'tasks_reg',   'text-info')    +
        kpiCard(d.total_success,  'successful',  'text-success') +
        kpiCard(d.total_failures, 'failed_runs', 'text-danger')  +
        kpiCard(d.uptime,         'uptime',      'text-warning');

      let cards = '';
      for (const [name, s] of Object.entries(d.tasks)) {
        cards += `<div class="col-md-6 col-lg-4"><div class="card p-3">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <span class="task-name">${name}</span>${badge(s.last_status||'pending')}
          </div>
          <div class="ts" style="line-height:1.8">
            ${t('last_run')} &nbsp;<span class="text-light">${s.last_run||'–'}</span><br>
            ${t('next_run')} &nbsp;<span class="text-light">${s.next_run||'–'}</span><br>
            ${t('total_runs')} &nbsp;<span class="text-light">${s.run_count||0}</span>
            &nbsp;|&nbsp; ${t('failures')} &nbsp;<span class="${(s.fail_count||0)>0?'text-danger':'text-light'}">${s.fail_count||0}</span>
          </div>
        </div></div>`;
      }
      document.getElementById('task-row').innerHTML = cards;
      document.getElementById('updated').textContent =
        t('updated') + ' ' + new Date().toLocaleTimeString();
    } catch(e) { console.error(e); }

    try {
      const r = await fetch('/api/logs?since=' + seen);
      const d = await r.json();
      if (d.logs && d.logs.length) {
        const el = document.getElementById('log-console');
        const atBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 30;
        for (const line of d.logs) {
          const div = document.createElement('div');
          div.textContent = line;
          if (line.includes('ERROR'))        div.className = 'err';
          else if (line.includes('WARNING')) div.className = 'warn';
          el.appendChild(div);
          seen++;
        }
        if (atBottom) el.scrollTop = el.scrollHeight;
      }
    } catch(e) {}
  }

  function clearConsole() {
    document.getElementById('log-console').innerHTML = '';
    seen = 0;
  }

  // Apply saved lang on load
  setLang(lang);
  setInterval(refresh, 3000);
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# API endpoints
# ---------------------------------------------------------------------------

@app.route("/")
def index() -> Response:
    return Response(DASHBOARD_HTML, mimetype="text/html")


@app.route("/api/status")
def api_status() -> Response:
    from engine.scheduler import scheduler  # late import avoids circular deps

    jobs = {job.id: job for job in scheduler.get_jobs()}

    enriched: dict = {}

    # Tasks that have already run
    for name, stats in task_stats.items():
        enriched[name] = dict(stats)
        job = jobs.get(name)
        if job and job.next_run_time:
            enriched[name]["next_run"] = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            enriched[name]["next_run"] = "–"

    # Tasks scheduled but not yet executed
    for job in scheduler.get_jobs():
        if job.id not in enriched:
            enriched[job.id] = {
                "last_status": "pending",
                "last_run": "–",
                "run_count": 0,
                "success_count": 0,
                "fail_count": 0,
                "next_run": job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
                if job.next_run_time
                else "–",
            }

    uptime = str(datetime.datetime.now() - start_time).split(".")[0]
    total_success = sum(s.get("success_count", 0) for s in task_stats.values())
    total_failures = sum(s.get("fail_count", 0) for s in task_stats.values())

    return jsonify(
        {
            "total_tasks": len(enriched),
            "total_success": total_success,
            "total_failures": total_failures,
            "uptime": uptime,
            "tasks": enriched,
        }
    )


@app.route("/api/logs")
def api_logs() -> Response:
    since = int(request.args.get("since", 0))
    all_logs = list(log_buffer)
    return jsonify({"logs": all_logs[since:], "total": len(all_logs)})


# ---------------------------------------------------------------------------
# Start in a daemon thread
# ---------------------------------------------------------------------------

def start_dashboard(host: str = "0.0.0.0", port: int = 8080) -> None:
    _setup_log_handler()
    t = threading.Thread(
        target=lambda: app.run(host=host, port=port, use_reloader=False),
        daemon=True,
        name="dashboard",
    )
    t.start()
    logging.info(f"Dashboard running -> http://localhost:{port}")
