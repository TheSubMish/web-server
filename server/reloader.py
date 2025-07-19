from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os, sys


class ReloadHandler(FileSystemEventHandler):
    def __init__(self, restart_func):
        self.restart_func = restart_func

    def on_any_event(self, event):
        # Restart the server on any code file change
        if event.src_path.endswith(".py"):
            print("Detected code change. Reloading server...")
            self.restart_func()


def start_with_reloader(main_func):
    def restart():
        print("Restarting server process...")
        os.execv(sys.executable, ["python"] + sys.argv)  # replace current process

    event_handler = ReloadHandler(restart)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()

    # Start the server in the main thread
    try:
        main_func()
    finally:
        observer.stop()
        observer.join()
