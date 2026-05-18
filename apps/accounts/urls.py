from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("verify/<str:token>/", views.verify_email_view, name="verify_email"),
    path("reset/", views.password_reset_request_view, name="password_reset_request"),
    path("reset/<str:token>/", views.password_reset_view, name="password_reset"),
    path("invite/", views.invite_view, name="invite"),
    path("invite/<str:token>/accept/", views.accept_invite_view, name="accept_invite"),
    path("profile/", views.profile_view, name="profile"),
    path("settings/", views.settings_view, name="settings"),
]
