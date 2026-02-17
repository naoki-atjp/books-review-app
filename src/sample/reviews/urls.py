from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("create/", views.ReviewCreateView.as_view(), name="create"),
    path("complete/", views.review_complete, name="complete"),
    path(
        "books/<str:book_id>/reviews/<int:review_id>/",
        views.review_detail,
        name="detail",
    ),

    # いいねトグル
    path(
        "books/<str:book_id>/reviews/<int:review_id>/like/",
        views.review_like_toggle,
        # views.review_like_dummy,
        name="like",
    ),
]