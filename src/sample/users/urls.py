from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = "users"

urlpatterns = [
    path("logout/", LogoutView.as_view(), name="logout"),
    path("mypage/", views.mypage_view, name="mypage"),
]