from django.contrib import admin
from django.urls import include, path

from core.views import HomeView
from users.views import (
    PasswordResetCompletePageView,
    PasswordResetConfirmPageView,
    login_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', login_view, name='login'),
    path(
        'accounts/reset/<uidb64>/<token>/',
        PasswordResetConfirmPageView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        'accounts/reset/done/',
        PasswordResetCompletePageView.as_view(),
        name='password_reset_complete',
    ),
    path('', HomeView.as_view(), name='home'),
    path('books/', include(('books.urls', 'books'), namespace='books')),
    path('reviews/', include(('reviews.urls', 'reviews'), namespace='reviews')),
    path('users/', include('users.urls')),
]
