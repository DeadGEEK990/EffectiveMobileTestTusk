from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import register


urlpatterns = [
    path("", views.main_page, name="Main page"),
    path("my-items/", views.my_items_page, name="My items"),
    path("my-requests/", views.my_request_page, name="My requests"),
    path(
        "received-requests/",
        views.my_received_requests_page,
        name="My received requests",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="ads/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),
]
