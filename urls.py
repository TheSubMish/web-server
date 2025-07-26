from server.urlhandler import UrlHandler

url_handler = UrlHandler()


def home_handler(request):
    return "Welcome to the home page!", 200


url_handler.add_route("/", home_handler)


def about_handler(request):
    return "This is the about page.", 200


url_handler.add_route("/about", about_handler)
