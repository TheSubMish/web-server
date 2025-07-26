def app(environ, start_response):
    path = environ.get("request", {}).get("path", "")
    method = environ.get("request", {}).get("method", "")
    query = environ.get("request", {}).get("query_params", {})

    start_response("200 OK", [("Content-Type", "text/plain")])

    return [f"Path: {path}\nMethod: {method}\nQuery: {query}".encode("utf-8")]
