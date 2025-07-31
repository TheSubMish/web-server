from typing import Callable, Dict, Any, List
from server.urlhandler import url_handler
from server.request import Request


def app(
    environ: Dict[str, Any], start_response: Callable[[str, List[tuple]], None]
) -> List[bytes]:
    """
    WSGI application entry point.

    Args:
        environ (Dict[str, Any]): The WSGI environment dictionary containing request data.
        start_response (Callable[[str, List[tuple]], None]): The WSGI callback for starting the HTTP response.

    Returns:
        List[bytes]: The response body as a list of byte strings, suitable for WSGI servers.

    Description:
        This function acts as the main WSGI application callable. It extracts the request object from the environment,
        determines the request path and method, and delegates handling to a URL handler. Depending on the type of response
        object returned, it either calls a custom `to_wsgi_response` method or constructs a standard WSGI response using
        status codes and headers.
    """

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
