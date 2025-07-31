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
            # Handle both <param> and <type:param> syntax
            regex_path: str = self._convert_path_to_regex(path)
            self.regex_routes[regex_path] = {
                "handler": handler,
                "methods": methods,
                "original_path": path,
                "param_types": self._extract_param_types(path),
            }
        else:
            self.routes[path] = {"handler": handler, "methods": methods}

    def _convert_path_to_regex(self, path: str) -> str:
        """Convert URL path with parameters to regex pattern"""

        type_patterns = {
            "int": r"\d+",
            "float": r"\d+\.\d+",
            "str": r"[^/]+",
        }

        # Replace typed parameters like <int:id>
        def typed_replacer(match):
            param_type, param_name = match.groups()
            pattern = type_patterns.get(param_type, r"[^/]+")
            return f"(?P<{param_name}>{pattern})"

        pattern = re.sub(r"<(int|float|str):(\w+)>", typed_replacer, path)

        # Replace untyped parameters like <id> (default to str)
        pattern = re.sub(r"<(\w+)>", r"(?P<\1>[^/]+)", pattern)
        
        print(pattern)

        return f"^{pattern}$"

    def _extract_param_types(self, path: str) -> Dict[str, str]:
        """Extract parameter types from path"""
        param_types = {}

        # Find <type:param> patterns
        typed_params = re.findall(r"<(int|float|str):(\w+)>", path)
        for param_type, param_name in typed_params:
            param_types[param_name] = param_type

        # Find simple <param> patterns (default to str)
        simple_params = re.findall(
            r"<(\w+)>", re.sub(r"<(?:int|float|str):\w+>", "", path)
        )
        for param_name in simple_params:
            if param_name not in param_types:
                param_types[param_name] = "str"

        return param_types

    def _convert_param_types(
        self, params: Dict[str, str], param_types: Dict[str, str]
    ) -> Dict[str, Any]:
        """Convert string parameters to their specified types"""
        converted = {}
        for name, value in params.items():
            param_type = param_types.get(name, "str")
            try:
                if param_type == "int":
                    converted[name] = int(value)
                elif param_type == "float":
                    converted[name] = float(value)
                else:
                    converted[name] = value
            except ValueError:
                converted[name] = value
        return converted

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
        try:

            print(self.regex_routes)

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
                        print()
                        print(route_info)
                        print()
                        url_params = match.groupdict()

                        if "param_types" in route_info:
                            url_params = self._convert_param_types(
                                url_params, route_info["param_types"]
                            )

                        request.url_params = url_params
                        result = route_info["handler"](request, **url_params)
                        return self._convert_to_response(result)
                    else:
                        return self.method_not_allowed(request)

            return self.not_found(request)

        except Exception as e:
            print(f"Error handling request: {e}")
            return self.server_error(request)

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
            status=404,  # Fixed: was 4, should be 404
        )

    def method_not_allowed(self, request: Request) -> Response:
        return Response(
            body="<h1>405 Method Not Allowed</h1><p>Method not allowed for this resource.</p>",
            status=405,
        )

    def server_error(self, request: Request) -> Response:
        return Response(
            body="<h1>500 Internal Server Error</h1><p>An unexpected error occurred.</p>",
            status=500,
        )


url_handler: UrlHandler = UrlHandler()
