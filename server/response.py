from typing import Callable, Any, Optional, List, Tuple
import json


class Response:
    """
    Represents an HTTP response for a WSGI web server.

    Attributes:
        body (str | dict): The response body, either as a string or a dictionary (for JSON responses).
        status (int): The HTTP status code of the response. Defaults to 200.
        headers (list[tuple[str, str]]): A list of (header, value) tuples for the response headers.
            Defaults to [('Content-Type', 'application/json')] if not provided.

    Methods:
        to_wsgi(start_response: Callable) -> list[bytes]:
            Converts the Response object into a WSGI-compatible response.
            Calls the provided start_response callable with the status and headers,
            and returns the response body as a list of bytes.
    """

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
    """
    Represents an HTTP response with a JSON body for WSGI applications.

    Args:
        data (Any): The data to be serialized as JSON in the response body.
        status (int, optional): The HTTP status code for the response. Defaults to 200.
        headers (Optional[List[Tuple[str, str]]], optional): Additional HTTP headers as a list of (name, value) tuples. Defaults to None.

    Attributes:
        data (Any): The response data to be serialized as JSON.
        status (int): The HTTP status code.
        headers (List[Tuple[str, str]]): The list of HTTP headers.

    Methods:
        to_wsgi_response(start_response):
            Serializes the response data to JSON, ensures appropriate headers are set,
            and returns the response in a format compatible with WSGI applications.
            Args:
                start_response (callable): The WSGI start_response callable.
            Returns:
                List[bytes]: The response body as a list containing a single bytes object.
    """

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
