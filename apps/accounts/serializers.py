"""
DRF serializers for the accounts API.
"""
from rest_framework import serializers
from .models import User, Organization, TeamInvite


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "website", "is_active", "created_at"]
        read_only_fields = ["id", "slug", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "full_name",
            "role", "organization", "email_verified", "avatar",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "email_verified", "created_at", "updated_at"]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    org_name = serializers.CharField(max_length=255)


class TeamInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamInvite
        fields = ["id", "email", "role", "accepted", "expires_at", "created_at"]
        read_only_fields = ["id", "accepted", "created_at"]
