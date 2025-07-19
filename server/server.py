import socket
import threading
import signal
import sys
import io


class Server:
    def __init__(self, app, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.app = app
        self._running = False
        signal.signal(signal.SIGINT, self._graceful_exit)

    def _graceful_exit(self, signum, frame):
        self.stop_server()
        sys.exit(0)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self._running = True
        print(f"Server started on {self.host}:{self.port}")

    def stop_server(self):
        self._running = False
        if self.server_socket:
            self.server_socket.close()

    def handle_client(self, client_socket):
        try:
            request_data = client_socket.recv(1024)
            if not request_data:
                client_socket.close()
                return

            request_lines = request_data.decode(errors="ignore").splitlines()
            if not request_lines:
                client_socket.close()
                return

            request_line = request_lines[0]
            try:
                method, path, _ = request_line.split()
            except ValueError:
                client_socket.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
                client_socket.close()
                return

            environ = {
                "REQUEST_METHOD": method,
                "PATH_INFO": path,
                "wsgi.version": (1, 0),
                "wsgi.url_scheme": "http",
                "wsgi.input": io.BytesIO(request_data),
                "wsgi.errors": sys.stderr,
                "wsgi.multithread": True,
                "wsgi.multiprocess": False,
                "wsgi.run_once": False,
                "SERVER_NAME": self.host,
                "SERVER_PORT": str(self.port),
            }

            headers_set = []

            def start_response(status, response_headers):
                headers_set[:] = [status, response_headers]

            response_body = self.app(environ, start_response)
            status, response_headers = headers_set

            response = f"HTTP/1.1 {status}\r\n"
            for header in response_headers:
                response += f"{header[0]}: {header[1]}\r\n"
            response += "\r\n"
            response = response.encode() + b"".join(response_body)
            client_socket.sendall(response)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

    def accept_connections(self):
        while self._running:
            if self.server_socket is None:
                break
            try:
                client_socket, addr = self.server_socket.accept()
            except OSError:
                break  # Socket closed
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.daemon = True
            thread.start()

    def run(self):
        self.start_server()
        try:
            self.accept_connections()
        except KeyboardInterrupt:
            self.stop_server()
