"""Base models for the Igar platform."""

import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
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


class TwoFactorResetEvent(BaseModel):
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="two_factor_reset_events",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_two_factor_resets",
    )

    class Meta:
        ordering = ("created_at", "id")

    def __str__(self):
        return f"2FA reset for user {self.target_user_id} at {self.created_at.isoformat()}"


# ============================================================================
# RBAC Models - Document Access Groups & Cloisonnement
# ============================================================================


class DocumentAccessGroup(BaseModel):
    """
    Groupe d'accès documentaire pour le cloisonnement.
    
    Permet de regrouper les documents par espaces documentaires (ex: Direction, Comptabilité, RH)
    et de restreindre l'accès par rôle/utilisateur.
    """

    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        ordering = ("name",)
        indexes = [
            models.Index(fields=("name",)),
            models.Index(fields=("parent",)),
        ]

    def __str__(self):
        return self.name


class UserDocumentAccessGroup(BaseModel):
    """
    Association many-to-many entre User et DocumentAccessGroup.
    
    Définit les groupes documentaires auxquels un utilisateur a accès.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="allowed_document_groups",
    )
    access_group = models.ForeignKey(
        DocumentAccessGroup,
        on_delete=models.CASCADE,
        related_name="users",
    )

    class Meta:
        unique_together = ("user", "access_group")
        ordering = ("user", "access_group")
        indexes = [
            models.Index(fields=("user", "access_group")),
            models.Index(fields=("access_group",)),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.access_group.name}"


class GroupDocumentAccessGroup(BaseModel):
    """
    Association many-to-many entre Group (rôle Django) et DocumentAccessGroup.
    
    Définit les groupes documentaires accessibles par un rôle.
    """

    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="allowed_document_groups",
    )
    access_group = models.ForeignKey(
        DocumentAccessGroup,
        on_delete=models.CASCADE,
        related_name="groups",
    )

    class Meta:
        unique_together = ("group", "access_group")
        ordering = ("group", "access_group")
        indexes = [
            models.Index(fields=("group", "access_group")),
            models.Index(fields=("access_group",)),
        ]

    def __str__(self):
        return f"{self.group.name} → {self.access_group.name}"


class AuditLogEntry(BaseModel):
    """
    Entrée de journal d'audit immuable pour traçabilité complète.
    
    Enregistre toutes les modifications de droits d'accès, utilisateurs, rôles.
    """

    ACTION_CHOICES = [
        ("user.created", "User créé"),
        ("user.modified", "User modifié"),
        ("user.deactivated", "User désactivé"),
        ("user.2fa_reset", "2FA réinitialisé"),
        ("role.created", "Rôle créé"),
        ("role.modified", "Rôle modifié"),
        ("role.deleted", "Rôle supprimé"),
        ("permission.assigned", "Permission assignée"),
        ("permission.revoked", "Permission révoquée"),
        ("document.access_denied", "Accès document refusé"),
        ("group.user_added", "Utilisateur ajouté au groupe"),
        ("group.user_removed", "Utilisateur retiré du groupe"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_log_entries",
    )
    action = models.CharField(max_length=32, choices=ACTION_CHOICES, db_index=True)
    resource_type = models.CharField(
        max_length=32,
        choices=[
            ("user", "Utilisateur"),
            ("role", "Rôle"),
            ("group", "Groupe"),
            ("document", "Document"),
            ("permission", "Permission"),
        ],
        db_index=True,
    )
    resource_id = models.IntegerField(db_index=True)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("-created_at",)),
            models.Index(fields=("user", "-created_at")),
            models.Index(fields=("action", "-created_at")),
            models.Index(fields=("resource_type", "resource_id")),
        ]

    def __str__(self):
        return f"{self.action} ({self.resource_type}:{self.resource_id}) by {self.user} at {self.created_at.isoformat()}"
