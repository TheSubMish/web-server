import sys

# Ensure run_server is properly imported and defined
try:
    from managements.command.runserver import run_server
except ImportError:
    run_server = None


class ExecuteCommand:

    def __init__(self, args):
        self.args = args

    def execute(self):
        if len(self.args) > 1 and self.args[1] == "runserver":

            try:
                host = self.args[2] if len(self.args) > 2 else "127.0.0.1"
                port = int(self.args[3]) if len(self.args) > 3 else 8000
                if callable(run_server):
                    run_server(host=host, port=port)
                else:
                    print("Error: run_server is not defined or not callable.")
                    sys.exit(1)
            except (IndexError, ValueError):
                host = "127.0.0.1"
                port = 8000

            if callable(run_server):
                run_server(host=host, port=port)

        else:
            print("Unknown command. Use 'runserver' to start the server.")
            sys.exit(1)
