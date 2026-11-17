from django.test import RequestFactory

from hello_world.views import hello_world


def test_hello_world_view_renders():
    request = RequestFactory().get("/hello_world/")
    response = hello_world(request)
    assert response.status_code == 200
