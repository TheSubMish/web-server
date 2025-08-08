import sys
from typing import List, Callable, Optional

# Ensure run_server is properly imported and defined
try:
    from managements.command.runserver import run_server
    from managements.command.makemigrations import makemigrations
except ImportError:
    run_server: Optional[Callable[[str, int], None]] = None
    makemigrations: Optional[Callable[[], None]] = None


class ExecuteCommand:

    def __init__(self, args: List[str]) -> None:
        self.args: List[str] = args

    def _run_server(self) -> None:
        try:
            host: str = self.args[2] if len(self.args) > 2 else "127.0.0.1"
            port: int = int(self.args[3]) if len(self.args) > 3 else 8000
            if callable(run_server):
                run_server(host, port)
            else:
                print("Error: run_server is not defined or not callable.")
                sys.exit(1)
        except (IndexError, ValueError):
            host: str = "127.0.0.1"
            port: int = 8000

        if callable(run_server):
            run_server(host, port)

    def execute(self) -> None:

        if not self.args or len(self.args) < 2:
            print("command not provided. Use 'runserver' to start the server.")
            sys.exit(1)

        commands: dict[str, Callable[[], None]] = {
            "runserver": self._run_server,
        }
        if makemigrations is not None:
            commands["makemigrations"] = makemigrations

        if self.args[1] not in commands.keys():
            print(f"Unknown command: {self.args[1]}")
            sys.exit(1)

        command: Callable[[], None] = commands[self.args[1]]
        command()
