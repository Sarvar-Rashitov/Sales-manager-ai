from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Proposal


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def proposal_list_api(request):
    proposals = Proposal.objects.filter(organization=request.user.organization).values(
        "id", "title", "status", "total_value", "created_at"
    )
    return Response(list(proposals))
