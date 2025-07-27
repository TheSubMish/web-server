from typing import Callable
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
            headers if headers else [("Content-Type", "text/html")]
        )

    def to_wsgi(self, start_response: Callable) -> list[bytes]:
        start_response(self.status, self.headers)
        content_type = dict(self.headers).get("Content-Type", "text/html")
        if isinstance(self.body, str):
            return [self.body.encode("utf-8")]
        if content_type == "application/json":
            return [json.dumps(self.body).encode("utf-8")]
        return [str(self.body).encode("utf-8")]
