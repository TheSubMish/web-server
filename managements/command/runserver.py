from server.server import Server
from server.reloader import start_with_reloader
from app import app


def run_server(host="127.0.0.1", port=8000):
    Server(app, host=host, port=port).run()

    start_with_reloader(run_server)
