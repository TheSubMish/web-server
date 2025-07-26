# server/reloader.py

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os, sys
import functools


class ReloadHandler(FileSystemEventHandler):
    def __init__(self, restart_func):
        self.restart_func = restart_func

    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            print("Detected code change. Reloading server...")
            self.restart_func()


def start_with_reloader(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        def restart():
            print("Restarting server process...")
            os.execv(sys.executable, ["python"] + sys.argv)

        event_handler = ReloadHandler(restart)
        observer = Observer()
        observer.schedule(event_handler, path=".", recursive=True)
        observer.start()

        try:
            return func(*args, **kwargs)
        finally:
            observer.stop()
            observer.join()

    return wrapper
