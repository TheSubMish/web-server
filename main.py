from typing import Any

from server.middleware import MiddlewareHandler
from server.response import Response, JSONResponse
from server.request import Request
from server.urlhandler import url_handler

from models import ContactModel


def home_handler(request: Request) -> JSONResponse:
    return JSONResponse(
        data={"json": "sending json data"},
        status=200,
        headers=[("Content-Type", "text/html"), ("X-Custom-Header", "Home-Page")],
    )


url_handler.get("/", home_handler)


def about_handler(request: Request) -> Response:
    return Response(body="<h1>About Us</h1><p>This is the about page.</p>", status=200)


url_handler.get("/about", about_handler)


def user_handler(request: Request, id: str) -> Response:
    if id:
        return Response(
            body=f"<h1>User Profile</h1><p>User profile for user {id}</p>", status=200
        )
    return Response(body="<h1>404 Not Found</h1><p>User not found</p>", status=404)


url_handler.get("/user/<id>", user_handler)


# Contact CRUD Handlers
def create_contact_handler(request: Request) -> JSONResponse:
    data: dict[str, Any] = request.data if request.data is not None else {}
    contact = ContactModel.objects.create(**data)
    return JSONResponse(
        data={"message": "Contact created successfully", "contact": contact.to_dict()},
        status=201,
        headers=[("Content-Type", "application/json")],
    )


url_handler.post("/contact", create_contact_handler)


def get_contact_handler(request: Request, id: int) -> JSONResponse:
    contact = ContactModel.objects.get(id)
    if contact:
        return JSONResponse(
            data={"contact": contact.to_dict()},
            status=200,
            headers=[("Content-Type", "application/json")],
        )
    return JSONResponse(
        data={"error": "Contact not found"},
        status=404,
        headers=[("Content-Type", "application/json")],
    )


url_handler.get("/contact/<id>", get_contact_handler)


def update_contact_handler(request: Request, id: int) -> JSONResponse:
    data: dict[str, Any] = request.data if request.data is not None else {}

    contact = ContactModel.objects.update(id, **data)
    if contact:
        return JSONResponse(
            data={
                "message": "Contact updated successfully",
                "contact": contact.to_dict(),
            },
            status=200,
            headers=[("Content-Type", "application/json")],
        )
    return JSONResponse(
        data={"error": "Contact not found"},
        status=404,
        headers=[("Content-Type", "application/json")],
    )


url_handler.put("/contact/<id>", update_contact_handler)


def delete_contact_handler(request: Request, id: int) -> JSONResponse:
    deleted = ContactModel.objects.delete(id)
    if deleted:
        return JSONResponse(
            data={"message": "Contact deleted successfully"},
            status=200,
            headers=[("Content-Type", "application/json")],
        )
    return JSONResponse(
        data={"error": "Contact not found"},
        status=404,
        headers=[("Content-Type", "application/json")],
    )


url_handler.delete("/contact/<id>", delete_contact_handler)


def list_contacts_handler(request: Request) -> JSONResponse:
    contacts = ContactModel.objects.all()
    contacts_list = [contact.to_dict() for contact in contacts]
    return JSONResponse(
        data={"contacts": contacts_list},
        status=200,
        headers=[("Content-Type", "application/json")],
    )


url_handler.get("/contacts", list_contacts_handler)


def user_update_handler(request: Request, id: str) -> JSONResponse:
    data = request.data

    if id:
        return JSONResponse(
            data={"message": f"User {id} updated successfully", "data": data},
            status=200,
            headers=[("Content-Type", "application/json")],
        )
    return JSONResponse(
        data={"error": "User ID is required"},
        status=400,
        headers=[("Content-Type", "application/json")],
    )


url_handler.put("/user/<id>/update", user_update_handler)


def user_partial_update_handler(request: Request, id: str) -> JSONResponse:

    data = request.data

    if id:
        return JSONResponse(
            data={"message": f"User {id} partially updated successfully", "data": data},
            status=200,
            headers=[("Content-Type", "application/json")],
        )

    return JSONResponse(
        data={"error": "User ID is required"},
        status=400,
        headers=[("Content-Type", "application/json")],
    )


url_handler.patch("/user/<id>/partial-update", user_partial_update_handler)


def user_delete_handler(request: Request, id: str) -> JSONResponse:
    if id:
        return JSONResponse(
            data={"message": f"User {id} deleted successfully"},
            status=200,
            headers=[("Content-Type", "application/json")],
        )
    return JSONResponse(
        data={"error": "User ID is required"},
        status=400,
        headers=[("Content-Type", "application/json")],
    )


url_handler.delete("/user/<id>/delete", user_delete_handler)


def get_double_param_check_handler(
    request: Request, number: int, name: str
) -> JSONResponse:
    if number and name:
        return JSONResponse(
            data={"message": f"Hello {name}, your number is {number}"},
            status=200,
            headers=[("Content-Type", "application/json")],
        )
    return JSONResponse(
        data={"error": "Invalid parameters"},
        status=400,
        headers=[("Content-Type", "application/json")],
    )


url_handler.get("/double/<number>/<name>", get_double_param_check_handler)


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


middlewares = [
    MiddlewareHandler,
    ResponseTimeMiddleware,
]


USE_SQLITE = True
