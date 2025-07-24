from managements.command.runserver import run_server
import sys


class ExecuteCommand:

    def __init__(self, args):
        self.args = args

    def execute(self):
        if len(self.args) > 1 and self.args[1] == "runserver":

            try:
                host = self.args[2] if len(self.args) > 2 else "127.0.0.1"
                port = int(self.args[3]) if len(self.args) > 3 else 8000
            except (IndexError, ValueError):
                host = "127.0.0.1"
                port = 8000

            run_server(host=host, port=port)

        else:
            print("Unknown command. Use 'runserver' to start the server.")
            sys.exit(1)
