from typing import Callable, Dict, Any, List
from server.urlhandler import url_handler


def app(
    environ: Dict[str, Any], start_response: Callable[[str, List[tuple]], None]
) -> List[bytes]:
    request: Dict[str, Any] = environ.get("request", {})
    path: str = request.get("path", "")

    response_obj = url_handler.handle_request(path, request)

    status_text: str = {
        200: "200 OK",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
        500: "500 Internal Server Error",
    }.get(int(response_obj.status), f"{response_obj.status} UNKNOWN")

    start_response(status_text, [("Content-Type", "text/plain")])

    return response_obj.to_wsgi(start_response=start_response)
