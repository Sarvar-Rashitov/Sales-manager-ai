"""
DRF API views for accounts.
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import UserSerializer, RegisterSerializer, TeamInviteSerializer
from .services import AuthService, InviteService


class RegisterAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = AuthService.register(**serializer.validated_data)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MeAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email_api(request):
    token = request.data.get("token", "")
    if AuthService.verify_email(token):
        return Response({"detail": "Email verified."})
    return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request_api(request):
    email = request.data.get("email", "")
    AuthService.request_password_reset(email)
    return Response({"detail": "If that email exists, a reset link was sent."})


@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_api(request):
    token = request.data.get("token", "")
    password = request.data.get("password", "")
    if AuthService.reset_password(token, password):
        return Response({"detail": "Password reset successfully."})
    return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_invite_api(request):
    email = request.data.get("email", "")
    role = request.data.get("role", "operator")
    try:
        invite = InviteService.send_invite(request.user, email, role)
        return Response(TeamInviteSerializer(invite).data, status=status.HTTP_201_CREATED)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
