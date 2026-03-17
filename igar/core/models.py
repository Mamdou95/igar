"""Base models for the Igar platform."""

import uuid

from django.db import models


class BaseModel(models.Model):
    """Abstract base model with UUID, created_at and updated_at fields."""

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
