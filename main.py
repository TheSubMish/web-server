from typing import Any

from server.middleware import MiddlewareHandler
from server.response import Response
from server.urlhandler import url_handler


def home_handler(request: Any) -> Response:
    return Response(
        body={"json": "sending json data"},
        status=200,
        headers=[("Content-Type", "text/html"), ("X-Custom-Header", "Home-Page")],
    )


url_handler.add_route("/", home_handler)


def about_handler(request: Any) -> Response:
    return Response(body="<h1>About Us</h1><p>This is the about page.</p>", status=200)


url_handler.add_route("/about", about_handler)


def user_handler(request: Any, id: str) -> Response:
    if id:
        return Response(
            body=f"<h1>User Profile</h1><p>User profile for user {id}</p>", status=200
        )
    return Response(body="<h1>404 Not Found</h1><p>User not found</p>", status=404)


url_handler.add_route("/user/<id>", user_handler)


class ResponseTimeMiddleware(MiddlewareHandler):
    def __init__(self, app: Any) -> None:
        self.app = app

    def __call__(self, environ: dict, start_response: Any) -> Any:
        import time

        start_time = time.time()
        response_body = self.app(environ, start_response)
        duration = time.time() - start_time

        print(f"Response Time: {duration:.4f} seconds")
        return response_body


middlewares = [
    MiddlewareHandler,
    ResponseTimeMiddleware,
]
