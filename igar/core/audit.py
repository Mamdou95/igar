"""Audit trail mixin and hash chain utilities."""

import json
import logging
from typing import Any, Dict, Optional

import structlog
from django.contrib.auth import get_user_model
from django.utils import timezone

from igar.core.models import AuditLogEntry

logger = structlog.get_logger(__name__)
User = get_user_model()


class AuditLogger:
    """Service pour enregistrer les événements dans l'audit trail."""

    @staticmethod
    def log(
        action: str,
        resource_type: str,
        resource_id: int,
        user: Optional[User] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        reason: str = "",
    ) -> AuditLogEntry:
        """
        Enregistre un événement dans l'audit trail.
        
        Args:
            action: Type d'action (ex: 'user.created', 'role.modified')
            resource_type: Type de ressource (ex: 'user', 'role', 'document')
            resource_id: ID de la ressource
            user: User qui a effectué l'action
            old_values: Ancien état de la ressource (JSON)
            new_values: Nouvel état de la ressource (JSON)
            ip_address: Adresse IP du client
            reason: Raison/description de l'action
            
        Returns:
            AuditLogEntry créée
        """
        entry = AuditLogEntry.objects.create(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user=user,
            old_values=old_values or {},
            new_values=new_values or {},
            ip_address=ip_address,
            reason=reason,
        )

        # Log aussi en structlog pour centralisation
        logger.info(
            "audit_event",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user.id if user else None,
            ip_address=ip_address,
            reason=reason,
        )

        return entry

    @staticmethod
    def get_logs(
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        user: Optional[User] = None,
        resource_id: Optional[int] = None,
        limit: int = 100,
    ) -> list:
        """Récupère les logs d'audit filtrés."""
        queryset = AuditLogEntry.objects.all()

        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        if action:
            queryset = queryset.filter(action=action)
        if user:
            queryset = queryset.filter(user=user)
        if resource_id:
            queryset = queryset.filter(resource_id=resource_id)

        return queryset.order_by("-created_at")[:limit]
