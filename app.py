from urls import url_handler


def app(environ, start_response):
    request = environ.get("request", {})
    path = request.get("path", "")

    response_body, status_code = url_handler.handle_request(path, request)

    # Prepare status string
    status_text = {
        200: "200 OK",
        404: "404 Not Found",
    }.get(status_code, f"{status_code} UNKNOWN")

    start_response(status_text, [("Content-Type", "text/plain")])

    return [response_body.encode("utf-8")]
