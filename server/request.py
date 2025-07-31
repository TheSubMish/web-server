from typing import Optional
import json


class Request:
    def __init__(
        self, method: str, path: str, headers: list[tuple[str, str]], body: bytes, data: Optional[dict] = None
    ):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.data = data
        self.query_params = self.parse_query_params()
        self.url_params: dict = {}

    def get_header(self, name: str) -> Optional[str]:
        for header in self.headers:
            if header[0].lower() == name.lower():
                return header[1]
        return None

    def get_query_param(self, name: str) -> Optional[str]:
        if "?" in self.path:
            query_string = self.path.split("?", 1)[1]
            params = dict(param.split("=") for param in query_string.split("&"))
            return params.get(name)
        return None

    def get_json_body(self) -> Optional[dict]:
        if self.get_header("Content-Type") == "application/json":

            try:
                return json.loads(self.body.decode("utf-8"))
            except json.JSONDecodeError:
                return None

        return None

    def parse_data(self) -> dict:
        """Parse the request body into a dictionary."""
        if self.body:
            try:
                return json.loads(self.body.decode("utf-8"))
            except json.JSONDecodeError:
                return {}
        return {}

    def parse_query_params(self) -> dict:
        """Parse the query parameters from the request path."""
        if "?" in self.path:
            query_string = self.path.split("?", 1)[1]
            return dict(param.split("=") for param in query_string.split("&"))
        return {}
