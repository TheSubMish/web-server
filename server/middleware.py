from typing import Callable, Any


class MiddlewareHandler:
    def __init__(self, app: Callable) -> None:
        self.app = app

    def __call__(self, environ: dict, start_response: Callable) -> Any:
        self.process_request(environ)

        # Wrap start_response to capture status
        status_holder = {}

        def custom_start_response(status, headers, exc_info=None):
            status_holder["status"] = status
            return start_response(status, headers, exc_info)

        response_body = self.app(environ, custom_start_response)
        self.process_response(status_holder.get("status", "Unknown"))
        return response_body

    def process_request(self, environ: dict) -> None:
        print(
            f"Request Method: {environ['REQUEST_METHOD']}, Path: {environ['PATH_INFO']}"
        )

    def process_response(self, status: str) -> None:
        print(f"Response Status: {status}")



def apply_middlewares(app, middlewares):
    for mw in reversed(middlewares):
        app = mw(app)
    return app
