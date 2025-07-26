import re
from typing import Callable, Dict, List, Optional, Any, Tuple


class UrlHandler:
    def __init__(self):
        self.routes: Dict[str, Dict[str, Any]] = {}
        self.regex_routes: Dict[str, Dict[str, Any]] = {}

    def add_route(
        self,
        path: str,
        handler: Callable[..., Any],
        methods: Optional[List[str]] = None,
    ) -> None:

        if methods is None:
            methods = ["GET"]

        if "<" in path and ">" in path:
            regex_path: str = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", path)
            regex_path = f"^{regex_path}$"
            self.regex_routes[regex_path] = {
                "handler": handler,
                "methods": methods,
                "original_path": path,
            }
        else:
            self.routes[path] = {"handler": handler, "methods": methods}

    def handle_request(
        self, path: str, request: Dict[str, Any], method: str = "GET"
    ) -> Any:
        if path in self.routes:
            route_info: Dict[str, Any] = self.routes[path]
            if method in route_info["methods"]:
                return route_info["handler"](request)

        for pattern, route_info in self.regex_routes.items():
            match: Optional[re.Match[str]] = re.match(pattern, path)
            if match:
                if method in route_info["methods"]:
                    request["url_params"] = match.groupdict()
                return route_info["handler"](request, **request.get("url_params", {}))
            else:
                return self.method_not_allowed(request)

        return self.not_found(request)

    def not_found(self, request: Dict[str, Any]) -> Tuple[str, int]:
        return "404 Not Found", 404

    def method_not_allowed(self, request: Dict[str, Any]) -> Tuple[str, int]:
        return "405 Method Not Allowed", 405


url_handler: UrlHandler = UrlHandler()
