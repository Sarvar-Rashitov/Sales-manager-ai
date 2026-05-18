from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import FollowUp
from .serializers import FollowUpSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def followup_list_api(request):
    followups = FollowUp.objects.filter(organization=request.user.organization)
    return Response(FollowUpSerializer(followups, many=True).data)
