from django.urls import path
from . import views
from django.http import HttpResponse

urlpatterns = [
    path("ping/", lambda request: HttpResponse("pong"), name="ping"),  
    path("categories/", views.category_list, name="category_list"),
    path("categories/new/", views.category_create, name="category_create"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_update"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
]

