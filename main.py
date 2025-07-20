from server.server import Server
from server.reloader import start_with_reloader
from app import app


if __name__ == "__main__":

    def run_server():
        # Your server.run() here
        Server(app).run()

    start_with_reloader(run_server)
