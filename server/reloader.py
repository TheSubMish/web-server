from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import os, sys
import functools
from typing import Callable, Any


class ReloadHandler(FileSystemEventHandler):
    def __init__(self, restart_func: Callable[[], None]) -> None:
        self.restart_func: Callable[[], None] = restart_func

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.src_path.endswith(".py"):
            print(f"Detected code change in {event.src_path}. Reloading server...")
            self.restart_func()


def start_with_reloader(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        def restart() -> None:
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
