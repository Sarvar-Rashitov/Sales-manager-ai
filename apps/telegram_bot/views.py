"""
Telegram views:
- Userbot account management (login flow)
- Bot API management (webhook setup)
- Broadcast management
- Inbox
"""
import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from .models import TelegramAccount, TelegramBot, TelegramMessage, Broadcast, BroadcastRecipient
from .services.session_service import SessionService
from .services.bot_service import BotService
from .services.broadcast_service import BroadcastService
from .forms import (
    TelegramAccountForm, VerifyCodeForm, Verify2FAForm,
    TelegramBotForm, BroadcastForm,
)

logger = logging.getLogger("apps.telegram_bot")


# ─────────────────────────────────────────────
# USERBOT
# ─────────────────────────────────────────────

@login_required
def account_list(request):
    accounts = TelegramAccount.objects.filter(organization=request.user.organization)
    bots = TelegramBot.objects.filter(organization=request.user.organization)
    return render(request, "telegram_bot/account_list.html", {
        "accounts": accounts,
        "bots": bots,
    })


@login_required
@require_http_methods(["GET", "POST"])
def account_add(request):
    form = TelegramAccountForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        account = form.save(commit=False)
        account.organization = request.user.organization
        account.added_by = request.user
        account.save()
        if SessionService.send_code(account):
            messages.success(request, f"Code sent to {account.phone_number}.")
            return redirect("telegram:verify_code", pk=account.pk)
        messages.error(request, "Failed to send code. Check Telegram API credentials in Settings.")
    return render(request, "telegram_bot/account_add.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def verify_code(request, pk):
    account = get_object_or_404(TelegramAccount, pk=pk, organization=request.user.organization)
    form = VerifyCodeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        result = SessionService.verify_code(account, form.cleaned_data["code"])
        if result.get("success"):
            messages.success(request, "Telegram account connected!")
            return redirect("telegram:account_list")
        elif result.get("needs_2fa"):
            return redirect("telegram:verify_2fa", pk=account.pk)
        messages.error(request, f"Verification failed: {result.get('error', 'Unknown error')}")
    return render(request, "telegram_bot/verify_code.html", {"form": form, "account": account})


@login_required
@require_http_methods(["GET", "POST"])
def verify_2fa(request, pk):
    account = get_object_or_404(TelegramAccount, pk=pk, organization=request.user.organization)
    form = Verify2FAForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if SessionService.verify_2fa(account, form.cleaned_data["password"]):
            messages.success(request, "2FA verified. Account connected!")
            return redirect("telegram:account_list")
        messages.error(request, "Invalid 2FA password.")
    return render(request, "telegram_bot/verify_2fa.html", {"form": form, "account": account})


@login_required
def disconnect_account(request, pk):
    account = get_object_or_404(TelegramAccount, pk=pk, organization=request.user.organization)
    SessionService.disconnect(account)
    messages.success(request, "Account disconnected.")
    return redirect("telegram:account_list")


# ─────────────────────────────────────────────
# BOT API
# ─────────────────────────────────────────────

@login_required
@require_http_methods(["GET", "POST"])
def bot_add(request):
    """Yangi Telegram Bot qo'shish."""
    form = TelegramBotForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        token = form.cleaned_data["bot_token"]
        # Token tekshiramiz
        info = BotService.get_bot_info(token)
        if not info.get("ok"):
            form.add_error("bot_token", f"Invalid token: {info.get('description', 'Unknown error')}")
        else:
            bot_data = info["result"]
            bot = form.save(commit=False)
            bot.organization = request.user.organization
            bot.added_by = request.user
            bot.bot_username = bot_data.get("username", "")
            bot.bot_id = bot_data.get("id")
            bot.save()
            messages.success(request, f"Bot @{bot.bot_username} added. Now set up the webhook.")
            return redirect("telegram:bot_webhook", pk=bot.pk)
    return render(request, "telegram_bot/bot_add.html", {"form": form})


@login_required
@require_http_methods(["GET", "POST"])
def bot_webhook_setup(request, pk):
    """Webhook URL o'rnatish."""
    bot = get_object_or_404(TelegramBot, pk=pk, organization=request.user.organization)
    if request.method == "POST":
        webhook_url = request.build_absolute_uri(f"/telegram/bot/{bot.pk}/webhook/")
        result = BotService.set_webhook(bot, webhook_url)
        if result.get("ok"):
            messages.success(request, f"Webhook set: {webhook_url}")
        else:
            messages.error(request, f"Webhook error: {result.get('description')}")
        return redirect("telegram:account_list")
    webhook_url = request.build_absolute_uri(f"/telegram/bot/{bot.pk}/webhook/")
    return render(request, "telegram_bot/bot_webhook.html", {"bot": bot, "webhook_url": webhook_url})


@login_required
def bot_delete_webhook(request, pk):
    bot = get_object_or_404(TelegramBot, pk=pk, organization=request.user.organization)
    BotService.delete_webhook(bot)
    messages.success(request, "Webhook removed.")
    return redirect("telegram:account_list")


@csrf_exempt
def bot_webhook_handler(request, pk):
    """
    Telegram Bot API webhook endpoint.
    POST /telegram/bot/<uuid>/webhook/
    CSRF exempt — Telegram serveridan keladi.
    """
    if request.method != "POST":
        return HttpResponse(status=405)

    try:
        bot = TelegramBot.objects.select_related("organization").get(pk=pk)
    except TelegramBot.DoesNotExist:
        return HttpResponse(status=404)

    # Webhook secret tekshiramiz
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if bot.webhook_secret and secret != bot.webhook_secret:
        logger.warning("Invalid webhook secret for bot %s", bot.pk)
        return HttpResponse(status=403)

    try:
        update = json.loads(request.body)
        BotService.process_webhook_update(bot, update)
    except Exception as e:
        logger.error("Webhook handler error: %s", e, exc_info=True)

    return HttpResponse("ok")


# ─────────────────────────────────────────────
# BROADCAST
# ─────────────────────────────────────────────

@login_required
def broadcast_list(request):
    broadcasts = Broadcast.objects.filter(
        organization=request.user.organization
    ).select_related("created_by")
    return render(request, "telegram_bot/broadcast_list.html", {"broadcasts": broadcasts})


@login_required
@require_http_methods(["GET", "POST"])
def broadcast_create(request):
    form = BroadcastForm(request.POST or None, org=request.user.organization)
    if request.method == "POST" and form.is_valid():
        broadcast = form.save(commit=False)
        broadcast.organization = request.user.organization
        broadcast.created_by = request.user
        broadcast.save()
        form.save_m2m()
        count = BroadcastService.prepare(broadcast)
        messages.success(request, f"Broadcast created. {count} recipients ready.")
        return redirect("telegram:broadcast_detail", pk=broadcast.pk)
    return render(request, "telegram_bot/broadcast_form.html", {"form": form, "action": "Create"})


@login_required
def broadcast_detail(request, pk):
    broadcast = get_object_or_404(Broadcast, pk=pk, organization=request.user.organization)
    recipients = broadcast.recipients.select_related("lead").order_by("status")[:50]
    return render(request, "telegram_bot/broadcast_detail.html", {
        "broadcast": broadcast,
        "recipients": recipients,
    })


@login_required
@require_http_methods(["POST"])
def broadcast_run(request, pk):
    """Broadcastni ishga tushiradi — sinxron."""
    broadcast = get_object_or_404(
        Broadcast, pk=pk, organization=request.user.organization,
        status__in=[Broadcast.Status.DRAFT, Broadcast.Status.CANCELLED]
    )
    # Qayta prepare qilamiz (yangi leadlar bo'lishi mumkin)
    BroadcastService.prepare(broadcast)
    result = BroadcastService.run(broadcast)
    messages.success(
        request,
        f"Broadcast completed: {result['sent']} sent, {result['failed']} failed."
    )
    return redirect("telegram:broadcast_detail", pk=pk)


@login_required
@require_http_methods(["POST"])
def broadcast_cancel(request, pk):
    broadcast = get_object_or_404(
        Broadcast, pk=pk, organization=request.user.organization,
        status=Broadcast.Status.RUNNING
    )
    BroadcastService.cancel(broadcast)
    messages.success(request, "Broadcast cancelled.")
    return redirect("telegram:broadcast_detail", pk=pk)


# ─────────────────────────────────────────────
# INBOX
# ─────────────────────────────────────────────

@login_required
def message_inbox(request):
    source_filter = request.GET.get("source", "")
    msgs = TelegramMessage.objects.filter(
        organization=request.user.organization
    ).select_related("account", "bot").order_by("-created_at")
    if source_filter:
        msgs = msgs.filter(source=source_filter)
    return render(request, "telegram_bot/inbox.html", {
        "messages": msgs[:100],
        "source_filter": source_filter,
    })
