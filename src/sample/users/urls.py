from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),
    path("password-reset/", views.password_reset_request_view, name="password_reset_request"),
    path("mypage/", views.mypage_view, name="mypage"),
]
