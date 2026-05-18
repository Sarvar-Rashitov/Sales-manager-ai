from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import TelegramAccount, TelegramMessage
from .serializers import TelegramAccountSerializer, TelegramMessageSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def account_list_api(request):
    accounts = TelegramAccount.objects.filter(organization=request.user.organization)
    return Response(TelegramAccountSerializer(accounts, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def message_list_api(request):
    msgs = TelegramMessage.objects.filter(
        organization=request.user.organization
    ).order_by("-created_at")[:50]
    return Response(TelegramMessageSerializer(msgs, many=True).data)
