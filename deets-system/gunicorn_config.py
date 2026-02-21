"""Gunicorn configuration for Render deployment."""
import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
bind = "0.0.0.0:10000"
timeout = 60
keepalive = 5
