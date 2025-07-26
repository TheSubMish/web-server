class UrlHandler:
    def __init__(self):
        self.routes = {}

    def add_route(self, path, handler):
        self.routes[path] = handler

    def handle_request(self, path, request):
        
        print(f"Handling request for path: {path}")
        print(f"Available routes: {self.routes.keys()}")
        
        if path in self.routes:
            return self.routes[path](request)
        else:
            return self.not_found(request)

    def not_found(self, request):
        return "404 Not Found", 404
