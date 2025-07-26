from server.urlhandler import url_handler
from typing import Any, Tuple


def home_handler(request: Any) -> Tuple[str, int]:
    return "Welcome to the home page!", 200


url_handler.add_route("/", home_handler)


def about_handler(request: Any) -> Tuple[str, int]:
    return "This is the about page.", 200


url_handler.add_route("/about", about_handler)


def user_handler(request: Any, id: str) -> Tuple[str, int]:
    if id:
        return f"User profile for user {id}", 200
    return "User not found", 404


url_handler.add_route("/user/<id>", user_handler)
