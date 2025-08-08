import sys
import importlib
import pkgutil
from typing import List, Callable, Optional, Dict


def discover_commands(package: str) -> Dict[str, Callable]:
    commands = {}
    pkg = importlib.import_module(package)
    for _, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
        if ispkg:
            continue
        module = importlib.import_module(f"{package}.{modname}")
        # Convention: command function has same name as module
        func = getattr(module, modname, None)
        if callable(func):
            commands[modname] = func
    return commands


class ExecuteCommand:

    def __init__(self, args: List[str]) -> None:
        self.args: List[str] = args
        self.commands: Dict[str, Callable] = discover_commands("managements.command")
        # Special handling for runserver to pass host/port
        if "runserver" in self.commands:
            self.commands["runserver"] = self._run_server

    def _run_server(self) -> None:
        run_server = getattr(
            importlib.import_module("managements.command.runserver"), "runserver", None
        )
        host: str = self.args[2] if len(self.args) > 2 else "127.0.0.1"
        port: int = int(self.args[3]) if len(self.args) > 3 else 8000
        if callable(run_server):
            run_server(host, port)
        else:
            print("Error: run_server is not defined or not callable.")
            sys.exit(1)

    def execute(self) -> None:
        if not self.args or len(self.args) < 2:
            print("command not provided. Use one of:", ", ".join(self.commands.keys()))
            sys.exit(1)

        cmd = self.args[1]
        if cmd not in self.commands:
            print(f"Unknown command: {cmd}")
            sys.exit(1)

        self.commands[cmd]()
