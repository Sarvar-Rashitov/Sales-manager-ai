from django.urls import path
from . import api_views

urlpatterns = [
    path("register/", api_views.RegisterAPIView.as_view(), name="api_register"),
    path("me/", api_views.MeAPIView.as_view(), name="api_me"),
    path("verify/", api_views.verify_email_api, name="api_verify_email"),
    path("password-reset/request/", api_views.password_reset_request_api, name="api_pw_reset_req"),
    path("password-reset/confirm/", api_views.password_reset_api, name="api_pw_reset"),
    path("invite/", api_views.send_invite_api, name="api_invite"),
]
