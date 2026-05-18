"""
Abstract base models shared across all apps.
"""
import uuid
from django.db import models


class TimeStampedModel(models.Model):
    """Adds created_at / updated_at to every model that inherits it."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """Uses UUID as primary key instead of integer."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """Combine UUID pk + timestamps — use this as the base for all models."""

    class Meta:
        abstract = True
