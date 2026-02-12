"""Gunicorn configuration file for production deployment.

Optimized for file conversion workloads with appropriate timeouts
and worker configuration based on available CPU cores.
"""
import multiprocessing
import os

# Server Socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker Processes
# Formula: (2 * CPU cores) + 1
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"  # sync es mejor para operaciones de I/O intensivas como conversiones
worker_connections = 1000
max_requests = 1000  # Restart worker after 1000 requests to prevent memory leaks
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once

# Timeouts
# Conversiones pueden tardar varios minutos
timeout = int(os.getenv('GUNICORN_TIMEOUT', '300'))  # 5 minutos
graceful_timeout = 30  # Tiempo para cerrar workers limpiamente
keepalive = 5  # Keep connections alive for 5 seconds

# Process Naming
proc_name = "file-converter-service"

# Server Mechanics
daemon = False  # Docker maneja el daemonization
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Management
preload_app = True  # Load application code before forking workers (saves RAM)

# Server Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Gunicorn server...")
    server.log.info(f"Workers: {workers}")
    server.log.info(f"Timeout: {timeout}s")

def on_reload(server):
    """Called to recycle workers during a reload."""
    server.log.info("Reloading workers...")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"Server ready. Listening on {bind}")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")

def pre_request(worker, req):
    """Called just before a worker processes the request."""
    worker.log.debug(f"{req.method} {req.path}")

def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    pass

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    worker.log.info(f"Worker received INT or QUIT signal (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info(f"Worker received SIGABRT signal (pid: {worker.pid})")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Shutting down Gunicorn server...")
