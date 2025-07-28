from server.server import Server
from server.reloader import start_with_reloader
from wsgi import app
from server.middleware import apply_middlewares

try:
    from main import middlewares
except ImportError:
    middlewares = []


@start_with_reloader
def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    def wsgi_app(environ, start_response):
        def start_response_wrapper(status, headers, exc_info=None):
            return start_response(status, headers)

        return app(environ, start_response_wrapper)

    Server(apply_middlewares(wsgi_app, middlewares), host=host, port=port).run()
