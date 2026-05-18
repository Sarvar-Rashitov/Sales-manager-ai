from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def conversation_list_api(request):
    convs = Conversation.objects.filter(organization=request.user.organization).values(
        "id", "status", "channel", "unread_count", "updated_at"
    )
    return Response(list(convs))
