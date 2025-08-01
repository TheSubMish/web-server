import json
import socket
import threading
from urllib.parse import parse_qs
from io import StringIO
import sys
import signal
from typing import Callable, Dict, Any, List, Tuple, Optional
from server.request import Request


class Server:
    """
    A simple multi-threaded WSGI-compatible HTTP server.

    This Server class listens for incoming HTTP connections, parses requests,
    creates WSGI environ dictionaries, and delegates request handling to a WSGI app.
    It supports graceful shutdown via SIGINT and handles each request in a separate thread.

    Attributes:
        wsgi_app (Callable): The WSGI application callable.
        host (str): The hostname or IP address to bind the server to.
        port (int): The port number to listen on.
        socket (Optional[socket.socket]): The server's listening socket.
        running (bool): Indicates if the server is running.

    Methods:
        __init__(wsgi_app, host, port): Initializes the server and sets up signal handling.
        
        _graceful_shutdown(signum, frame): Handles graceful shutdown on SIGINT.
        
        start_server(): Initializes and starts the server socket.
        
        accept_connections(): Accepts incoming connections and spawns threads for requests.
        
        handle_request(client_socket): Handles an individual HTTP request.
        
        create_wsgi_environ(method, path, query_string, headers, raw_request): Builds WSGI environ dict.
        
        parse_json(body, content_type): Parses JSON body if content type is application/json.
        
        send_response(client_socket, response_data, response_body): Sends HTTP response to client.
        
        stop_server(): Stops the server and closes the socket.
        
        run(): Starts the server and begins accepting connections.
    """
    def __init__(
        self,
        wsgi_app: Callable[
            [
                Dict[str, Any],
                Callable[[str, List[Tuple[str, str]], Optional[Any]], None],
            ],
            List[Any],
        ],
        host: str = "127.0.0.1",
        port: int = 8000,
    ) -> None:
        self.wsgi_app: Callable[
            [
                Dict[str, Any],
                Callable[[str, List[Tuple[str, str]], Optional[Any]], None],
            ],
            List[Any],
        ] = wsgi_app
        self.host: str = host
        self.port: int = port
        self.socket: Optional[socket.socket] = None
        self.running: bool = False
        signal.signal(signal.SIGINT, self._graceful_shutdown)

    def _graceful_shutdown(self, signum: int, frame: Any) -> None:
        """Handle graceful shutdown on signal"""
        print("Shutting down server gracefully...")
        self.stop_server()
        sys.exit(0)

    def start_server(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.running = True
        print(f"Server running on http://{self.host}:{self.port}")
        try:
            import main
        except ImportError:
            pass

    def accept_connections(self) -> None:
        if self.socket is None:
            raise RuntimeError(
                "Server socket is not initialized. Call start_server() first."
            )

        while self.running:
            try:
                client_socket, address = self.socket.accept()
                # Handle each request in a separate thread
                thread: threading.Thread = threading.Thread(
                    target=self.handle_request, args=(client_socket,)
                )
                thread.daemon = True
                thread.start()
            except OSError:
                break

    def handle_request(self, client_socket: socket.socket) -> None:
        try:
            # Receive HTTP request
            request_data: str = client_socket.recv(1024).decode("utf-8")

            if not request_data:
                return

            # Parse HTTP request
            lines: List[str] = request_data.split("\n")
            request_line: str = lines[0]
            method: str
            path: str
            version: str
            method, path, version = request_line.split()

            # Extract query string
            query_string: str
            if "?" in path:
                path, query_string = path.split("?", 1)
            else:
                query_string = ""

            # Parse headers
            headers: Dict[str, str] = {}
            for line in lines[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.strip().upper().replace("-", "_")] = value.strip()

            # Create WSGI environ
            environ: Dict[str, Any] = self.create_wsgi_environ(
                method, path, query_string, headers, request_data
            )

            response_data: List[Any] = []

            def start_response(
                status: str,
                response_headers: List[Tuple[str, str]],
                exc_info: Optional[Any] = None,
            ) -> None:
                response_data.extend([status, response_headers])

            # Get response from WSGI app
            response_body: List[Any] = self.wsgi_app(environ, start_response)

            # Send HTTP response
            self.send_response(client_socket, response_data, response_body)

        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            client_socket.close()

    def create_wsgi_environ(
        self,
        method: str,
        path: str,
        query_string: str,
        headers: Dict[str, str],
        raw_request: str,
    ) -> Dict[str, Any]:

        content_length = int(headers.get("CONTENT_LENGTH", "0"))

        body = ""
        if content_length > 0:
            header_end = raw_request.find("\r\n\r\n")
            if header_end != -1:
                body = raw_request[header_end + 4 :]
                # Ensure we have the full body
                if self.socket and len(body.encode("utf-8")) < content_length:
                    # Read additional data if needed
                    remaining = content_length - len(body.encode("utf-8"))
                    body += self.socket.recv(remaining).decode(
                        "utf-8", errors="replace"
                    )

        data = self.parse_json(body, headers.get("CONTENT_TYPE", ""))

        request: Request = Request(
            method=method,
            path=path,
            headers=list(headers.items()),
            body=raw_request.encode("utf-8"),
            data=data,
        )

        """Create WSGI environ dictionary"""
        environ: Dict[str, Any] = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "QUERY_STRING": query_string,
            "CONTENT_TYPE": headers.get("CONTENT_TYPE", ""),
            "CONTENT_LENGTH": headers.get("CONTENT_LENGTH", ""),
            "SERVER_NAME": self.host,
            "SERVER_PORT": str(self.port),
            "SERVER_PROTOCOL": "HTTP/1.1",
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "http",
            "wsgi.input": StringIO(),  # For POST data
            "wsgi.errors": sys.stderr,
            "wsgi.multithread": True,
            "wsgi.multiprocess": False,
            "wsgi.run_once": False,
            "request": request,
        }

        # Add HTTP headers to environ
        for key, value in headers.items():
            if key not in ("CONTENT_TYPE", "CONTENT_LENGTH"):
                environ[f"HTTP_{key}"] = value

        return environ

    def parse_json(self, body: str, content_type: str) -> Optional[Dict[str, Any]]:
        """Parse JSON body if content type is application/json"""
        if "application/json" in content_type.lower() and body.strip():
            try:
                return json.loads(body)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                return None
        return None

    def send_response(
        self,
        client_socket: socket.socket,
        response_data: List[Any],
        response_body: List[Any],
    ) -> None:
        """Send HTTP response back to client"""
        status: str = response_data[0]
        headers: List[Tuple[str, str]] = response_data[1]

        # Check if Content-Type is application/json
        is_json = any(
            header_name.lower() == "content-type"
            and "application/json" in header_value.lower()
            for header_name, header_value in headers
        )

        # Build HTTP response
        response: str = f"HTTP/1.1 {status}\r\n"
        for header_name, header_value in headers:
            response += f"{header_name}: {header_value}\r\n"
        response += "\r\n"  # End of headers

        # Send response headers
        client_socket.send(response.encode("utf-8"))

        # Send response body
        for data in response_body:
            if is_json and not isinstance(data, (bytes, bytearray)):
                # Serialize to JSON if not already bytes
                client_socket.send(json.dumps(data).encode("utf-8"))
            elif isinstance(data, str):
                client_socket.send(data.encode("utf-8"))
            else:
                client_socket.send(data)

    def stop_server(self) -> None:
        self.running = False
        if self.socket:
            self.socket.close()
        print("Server stopped")

    def run(self) -> None:
        self.start_server()
        try:
            self.accept_connections()
        except KeyboardInterrupt:
            self.stop_server()
