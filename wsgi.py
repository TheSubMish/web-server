from typing import Callable, Dict, Any, List
from server.urlhandler import url_handler
from server.request import Request


def app(
    environ: Dict[str, Any], start_response: Callable[[str, List[tuple]], None]
) -> List[bytes]:
    request: Request = environ.get("request", {})
    path: str = request.path
    method: str = request.method.upper()

    response_obj = url_handler.handle_request(path, request, method)

    # If it's a JSONResponse, use its method
    if hasattr(response_obj, "to_wsgi_response"):
        return response_obj.to_wsgi_response(start_response)

    # Otherwise, assume it's a normal Response
    status_text: str = {
        200: "200 OK",
        201: "201 Created",
        404: "404 Not Found",
        405: "405 Method Not Allowed",
        500: "500 Internal Server Error",
    }.get(int(response_obj.status), f"{response_obj.status} UNKNOWN")

    start_response(status_text, response_obj.headers)
    return response_obj.to_wsgi(start_response=start_response)
