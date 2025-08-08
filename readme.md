# Web Server & Framework Mashup

This project aims to build a Python web server and framework inspired by both **Django** and **FastAPI**. The goal is to combine the best features of both frameworks, providing a modern, fast, and flexible foundation for web development.

## Status

🚧 **Under Construction**  
The project is in its early stages. Core features and architecture are actively being developed.

## Vision

- **Django-like structure:** Emphasize modularity, reusability, and convention-over-configuration.
- **FastAPI-like speed:** Leverage async capabilities for high performance and scalability.
- **Developer Experience:** Simple, intuitive APIs and tooling.

## Getting Started

Stay tuned! Setup instructions and usage examples will be added as development progresses.

## Installation & Usage

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Start the development server:**

   ```bash
   python manage.py runserver
   ```

The server will start and be accessible at `http://127.0.0.1:8000/` by default.

3. **Create a main file**

   ```bash
   touch main.py
   ```

4. **Creating a view:**

   ```python

   from server.response import Response
   from server.urlhandler import url_handler

   def home_page(request):
       return Response(
           body={"json": "sending json data"},
           status=200,
           headers=[("Content-Type", "application/json")],
       )
   ```

5. **Add url**

   ```python
   from server.urlhandler import url_handler
   url_handler.add_route("/", home_page)
   ```

6. **Add middleware**

   ```python
   from server.middleware import MiddlewareHandler
   class ResponseTimeMiddleware(MiddlewareHandler):
      def __init__(self, app: Any) -> None:
        self.app = app

      def __call__(self, environ: dict, start_response: Any) -> Any:
         import time

         start_time = time.time()
         response_body = self.app(environ, start_response)
         duration = time.time() - start_time

         print(f"Response Time: {duration:.4f} seconds")
         return response_body
   ```

   **Append to list**

   ```python
   middlewares = [
      MiddlewareHandler,
      ResponseTimeMiddleware,
   ]
   ```

7. **Create Models**

   ```python
   from server.db.models import Model
   from sqlalchemy import Column, String

   class ContactModel(Model):

      __tablename__ = "contacts"

      name = Column(String, nullable=False)
      email = Column(String, nullable=False)
      message = Column(String, nullable=False)
   ```

8. **Make migrations files**
   ```bash
   python manage.py makemigrations
   ```

## Contributing

Contributions and feedback are welcome. Please open issues or pull requests to help shape the project.

## License

To be determined.
