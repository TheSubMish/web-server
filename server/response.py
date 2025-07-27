from typing import Callable


class Response:
    def __init__(
        self,
        body: str = "",
        status: int = 200,
        headers: list[tuple[str, str]] = [],
    ) -> None:
        self.body: str = body
        self.status: int = status
        self.headers: list[tuple[str, str]] = (
            headers if headers else [("Content-Type", "text/html")]
        )

    def to_wsgi(self, start_response: Callable) -> list[bytes]:
        start_response(self.status, self.headers)
        if isinstance(self.body, str):
            return [self.body.encode("utf-8")]
        return [self.body]
