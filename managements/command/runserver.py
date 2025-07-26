from server.server import Server
from server.reloader import start_with_reloader
from wsgi import app


@start_with_reloader
def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    def wsgi_app(environ, start_response):
        def start_response_wrapper(status, headers, exc_info=None):
            return start_response(status, headers)

        return app(environ, start_response_wrapper)

    Server(wsgi_app, host=host, port=port).run()
