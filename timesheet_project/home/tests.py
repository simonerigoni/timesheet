from django.test import RequestFactory

from home.views import home, welcome


def test_home_and_welcome_views_render():
    factory = RequestFactory()
    assert home(factory.get("/")).status_code == 200
    assert welcome(factory.get("/welcome/")).status_code == 200
