from typing import Optional
import json


class Request:
    """
    Represents an HTTP request.

    Attributes:
        method (str): The HTTP method (e.g., 'GET', 'POST').
        path (str): The request path, possibly including query parameters.
        headers (list[tuple[str, str]]): A list of (header_name, header_value) tuples.
        body (bytes): The raw request body.
        data (Optional[dict]): Parsed data from the request body, if available.
        query_params (dict): Dictionary of parsed query parameters from the path.
        url_params (dict): Dictionary of URL parameters, to be set externally.

    Methods:
        get_header(name: str) -> Optional[str]:
            Retrieve the value of a header by name (case-insensitive).

        get_query_param(name: str) -> Optional[str]:
            Retrieve the value of a query parameter by name.

        get_json_body() -> Optional[dict]:
            Parse and return the JSON body if the Content-Type is 'application/json'.

        parse_data() -> dict:
            Parse the request body as JSON and return a dictionary.

        parse_query_params() -> dict:
            Parse and return the query parameters from the request path as a dictionary.
    """

    def __init__(
        self,
        method: str,
        path: str,
        headers: list[tuple[str, str]],
        body: bytes,
        data: Optional[dict] = None,
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
