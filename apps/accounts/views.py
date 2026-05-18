"""
Accounts views — register, login, logout, verify, reset, invite, settings.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .forms import (
    RegisterForm, LoginForm, PasswordResetRequestForm,
    PasswordResetForm, InviteForm, AcceptInviteForm,
    OrganizationSettingsForm,
)
from .models import OrganizationSettings
from .services import AuthService, InviteService


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            AuthService.register(
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                org_name=form.cleaned_data["org_name"],
            )
            messages.success(request, "Account created! Check your email to verify.")
            return redirect("accounts:login")
        except ValueError as e:
            form.add_error(None, str(e))
    return render(request, "accounts/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:index")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        if user:
            login(request, user)
            return redirect(request.GET.get("next", "dashboard:index"))
        form.add_error(None, "Invalid email or password.")
    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


def verify_email_view(request, token: str):
    if AuthService.verify_email(token):
        messages.success(request, "Email verified! You can now log in.")
    else:
        messages.error(request, "Invalid or expired verification link.")
    return redirect("accounts:login")


@require_http_methods(["GET", "POST"])
def password_reset_request_view(request):
    form = PasswordResetRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        AuthService.request_password_reset(form.cleaned_data["email"])
        messages.success(request, "If that email exists, a reset link has been sent.")
        return redirect("accounts:login")
    return render(request, "accounts/password_reset_request.html", {"form": form})


@require_http_methods(["GET", "POST"])
def password_reset_view(request, token: str):
    form = PasswordResetForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if AuthService.reset_password(token, form.cleaned_data["password"]):
            messages.success(request, "Password reset! Please log in.")
            return redirect("accounts:login")
        messages.error(request, "Invalid or expired reset link.")
    return render(request, "accounts/password_reset.html", {"form": form, "token": token})


@login_required
@require_http_methods(["GET", "POST"])
def invite_view(request):
    form = InviteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            InviteService.send_invite(
                invited_by=request.user,
                email=form.cleaned_data["email"],
                role=form.cleaned_data["role"],
            )
            messages.success(request, "Invitation sent.")
            return redirect("accounts:invite")
        except ValueError as e:
            form.add_error(None, str(e))
    return render(request, "accounts/invite.html", {"form": form})


@require_http_methods(["GET", "POST"])
def accept_invite_view(request, token: str):
    form = AcceptInviteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            user = InviteService.accept_invite(
                token=token,
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
            )
            login(request, user)
            messages.success(request, "Welcome to the team!")
            return redirect("dashboard:index")
        except ValueError as e:
            form.add_error(None, str(e))
    return render(request, "accounts/accept_invite.html", {"form": form, "token": token})


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html", {"user": request.user})


# ─────────────────────────────────────────────
# SETTINGS — Kompaniya sozlamalari
# ─────────────────────────────────────────────

@login_required
@require_http_methods(["GET", "POST"])
def settings_view(request):
    """
    Kompaniya sozlamalari sahifasi.
    Owner va Admin ko'ra oladi va o'zgartira oladi.
    """
    if not request.user.organization:
        messages.error(request, "You are not part of any organization.")
        return redirect("dashboard:index")

    if request.user.role not in ("owner", "admin"):
        messages.error(request, "Only Owner or Admin can change settings.")
        return redirect("dashboard:index")

    org = request.user.organization
    obj, _ = OrganizationSettings.objects.get_or_create(organization=org)

    form = OrganizationSettingsForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Settings saved successfully.")
        return redirect("accounts:settings")

    return render(request, "accounts/settings.html", {
        "form": form,
        "org": org,
        "settings_obj": obj,
    })
