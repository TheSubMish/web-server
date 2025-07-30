from typing import Callable, Any, Optional, List, Tuple
import json


class Response:
    def __init__(
        self,
        body: str | dict = "",
        status: int = 200,
        headers: list[tuple[str, str]] = [],
    ) -> None:
        self.body: str | dict = body
        self.status: int = status
        self.headers: list[tuple[str, str]] = (
            headers if headers else [("Content-Type", "application/json")]
        )

    def to_wsgi(self, start_response: Callable) -> list[bytes]:
        start_response(self.status, self.headers)
        content_type = dict(self.headers).get("Content-Type", "text/html")
        if isinstance(self.body, str):
            return [self.body.encode("utf-8")]
        if content_type == "application/json":
            return [json.dumps(self.body).encode("utf-8")]
        return [str(self.body).encode("utf-8")]


class JSONResponse:
    def __init__(
        self,
        data: Any,
        status: int = 200,
        headers: Optional[List[Tuple[str, str]]] = None,
    ):
        self.data = data
        self.status = status
        self.headers = headers or []

        # Ensure Content-Type is always application/json
        content_type_set = any(h[0].lower() == "content-type" for h in self.headers)
        if not content_type_set:
            self.headers.append(("Content-Type", "application/json"))

    def to_wsgi_response(self, start_response):
        json_data = json.dumps(self.data, indent=2)

        # Add Content-Length header
        content_length_set = any(h[0].lower() == "content-length" for h in self.headers)
        if not content_length_set:
            self.headers.append(("Content-Length", str(len(json_data.encode("utf-8")))))

        start_response(self.status, self.headers)
        return [json_data.encode("utf-8")]
