from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),
    path("signup/verification-sent/", views.signup_verification_sent_view, name="signup_verification_sent"),
    path("verify-email/<uidb64>/<token>/", views.verify_email_view, name="verify_email"),
    path("password-reset/", views.PasswordResetRequestView.as_view(), name="password_reset"),
    path("password-reset/done/", views.PasswordResetDonePageView.as_view(), name="password_reset_done"),
    path("mypage/", views.mypage_view, name="mypage"),
]
