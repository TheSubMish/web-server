import re


class UrlHandler:
    def __init__(self):
        self.routes = {}
        self.regex_routes = {}

    def add_route(self, path, handler, methods=None):

        if methods is None:
            methods = ["GET"]

        if "<" in path and ">" in path:
            regex_path = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", path)
            regex_path = f"^{regex_path}$"
            self.regex_routes[regex_path] = {
                "handler": handler,
                "methods": methods,
                "original_path": path,
            }
        else:
            self.routes[path] = {"handler": handler, "methods": methods}

    def handle_request(self, path, request, method="GET"):
        if path in self.routes:
            route_info = self.routes[path]
            if method in route_info["methods"]:
                return route_info["handler"](request)

        for pattern, route_info in self.regex_routes.items():
            match = re.match(pattern, path)
            if match:
                if method in route_info["methods"]:
                    # Add URL parameters to request
                    request.url_params = match.groupdict()
                return route_info["handler"](request)
            else:
                return self.method_not_allowed(request)

        return self.not_found(request)

    def not_found(self, request):
        return "404 Not Found", 404

    def method_not_allowed(self, request):
        return "405 Method Not Allowed", 405
