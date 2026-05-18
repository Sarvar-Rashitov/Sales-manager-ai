from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(
        organization=request.user.organization
    ).select_related("lead", "assigned_to")
    return render(request, "messaging/inbox.html", {"conversations": conversations})


@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(
        Conversation, pk=pk, organization=request.user.organization
    )
    messages = conversation.messages.order_by("created_at")
    return render(request, "messaging/conversation.html", {
        "conversation": conversation,
        "messages": messages,
    })
