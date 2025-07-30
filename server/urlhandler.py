import re
from typing import Callable, Dict, List, Optional, Any

from server.response import Response, JSONResponse
from server.request import Request


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

    def get(self, path: str, handler: Callable):
        """Add GET route"""
        self.add_route(path, handler, ["GET"])

    def post(self, path: str, handler: Callable):
        """Add POST route"""
        self.add_route(path, handler, ["POST"])

    def put(self, path: str, handler: Callable):
        """Add PUT route"""
        self.add_route(path, handler, ["PUT"])

    def patch(self, path: str, handler: Callable):
        """Add PATCH route"""
        self.add_route(path, handler, ["PATCH"])

    def delete(self, path: str, handler: Callable):
        """Add DELETE route"""
        self.add_route(path, handler, ["DELETE"])

    def handle_request(
        self, path: str, request: Request, method: str = "GET"
    ) -> Response:
        if path in self.routes:
            route_info: Dict[str, Any] = self.routes[path]
            if method in route_info["methods"]:
                result = route_info["handler"](request)
                return self._convert_to_response(result)

            else:
                return self.method_not_allowed(request)

        for pattern, route_info in self.regex_routes.items():
            match: Optional[re.Match[str]] = re.match(pattern, path)
            if match:
                if method in route_info["methods"]:

                    result = route_info["handler"](request, **request.query_params)
                    return self._convert_to_response(result)
            else:
                return self.method_not_allowed(request)

        return self.not_found(request)

    def _convert_to_response(self, result: Any) -> Response:

        if isinstance(result, Response):
            return result
        elif hasattr(result, "to_wsgi_response"):
            return result
        elif isinstance(result, tuple):
            if len(result) == 2:
                body, status_code = result
                return Response(body=body, status=status_code)
            elif len(result) == 3:
                body, status_code, headers = result
                return Response(body=body, status=status_code, headers=headers)
            else:
                return Response(body=str(result))
        elif isinstance(result, str):
            return Response(body=result)
        else:
            return Response(body=str(result))

    def not_found(self, request: Request) -> Response:
        return Response(
            body="<h1>404 Not Found</h1><p>The requested page was not found.</p>",
            status=4,
        )

    def method_not_allowed(self, request: Request) -> Response:
        return Response(
            body="<h1>405 Method Not Allowed</h1><p>Method not allowed for this resource.</p>",
            status=405,
        )


url_handler: UrlHandler = UrlHandler()
