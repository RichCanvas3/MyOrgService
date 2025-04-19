from ninja import NinjaAPI

api = NinjaAPI(title="myorgservice", version="2.0.0")
apis = [
]

@api.get("/hello")
def hello(request):
    return "Hello world"