import socket
import threading
from urllib.parse import parse_qs
from io import StringIO
import sys
import signal


class Server:
    def __init__(self, wsgi_app, host="127.0.0.1", port=8000):
        self.wsgi_app = wsgi_app
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        signal.signal(signal.SIGINT, self._graceful_shutdown)

    def _graceful_shutdown(self, signum, frame):
        """Handle graceful shutdown on signal"""
        print("Shutting down server gracefully...")
        self.stop_server()
        sys.exit(0)

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.running = True
        print(f"Server running on http://{self.host}:{self.port}")
        import main

    def accept_connections(self):

        if self.socket is None:
            raise RuntimeError(
                "Server socket is not initialized. Call start_server() first."
            )

        while self.running:
            try:
                client_socket, address = self.socket.accept()
                # Handle each request in a separate thread
                thread = threading.Thread(
                    target=self.handle_request, args=(client_socket,)
                )
                thread.daemon = True
                thread.start()
            except OSError:
                break

    def handle_request(self, client_socket):
        try:
            # Receive HTTP request
            request_data = client_socket.recv(1024).decode("utf-8")

            if not request_data:
                return

            # Parse HTTP request
            lines = request_data.split("\n")
            request_line = lines[0]
            method, path, version = request_line.split()

            # Extract query string
            if "?" in path:
                path, query_string = path.split("?", 1)
            else:
                query_string = ""

            # Parse headers
            headers = {}
            for line in lines[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.strip().upper().replace("-", "_")] = value.strip()

            # Create WSGI environ
            environ = self.create_wsgi_environ(
                method, path, query_string, headers, request_data
            )

            # Call WSGI application
            response_data = []

            def start_response(status, response_headers, exc_info=None):
                response_data.extend([status, response_headers])

            # Get response from WSGI app
            response_body = self.wsgi_app(environ, start_response)

            # Send HTTP response
            self.send_response(client_socket, response_data, response_body)
            
            print(f"{method} {path} - {response_data[0]}")

        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            client_socket.close()

    def create_wsgi_environ(self, method, path, query_string, headers, raw_request):

        query_dict = parse_qs(query_string)

        request = {
            "method": method,
            "path": path,
            "query_params": query_dict,
            "HTTP_HEADERS": headers,
            "RAW_REQUEST": raw_request,
        }

        """Create WSGI environ dictionary"""
        environ = {
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

    def send_response(self, client_socket, response_data, response_body):
        """Send HTTP response back to client"""
        status = response_data[0]
        headers = response_data[1]

        # Build HTTP response
        response = f"HTTP/1.1 {status}\r\n"

        for header_name, header_value in headers:
            response += f"{header_name}: {header_value}\r\n"

        response += "\r\n"  # End of headers

        # Send response headers
        client_socket.send(response.encode("utf-8"))

        # Send response body
        for data in response_body:
            if isinstance(data, str):
                client_socket.send(data.encode("utf-8"))
            else:
                client_socket.send(data)

    def stop_server(self):
        self.running = False
        if self.socket:
            self.socket.close()
        print("Server stopped")

    def run(self):
        self.start_server()
        try:
            self.accept_connections()
        except KeyboardInterrupt:
            self.stop_server()
