"""Decorators and helpers for document access enforcement."""

from functools import wraps
from typing import Any

from django.db.models import Q
from django.http import Http404
from rest_framework.permissions import BasePermission


def _get_user_document_groups(user):
    allowed_groups_manager = getattr(user, 'allowed_document_groups', None)
    if allowed_groups_manager is None:
        return None

    user_group_queryset = allowed_groups_manager.all()

    # `allowed_document_groups` can be either a direct M2M to DocumentAccessGroup
    # or a reverse FK manager to UserDocumentAccessGroup (through model).
    if hasattr(user_group_queryset.model, 'access_group_id'):
        return user_group_queryset.values_list('access_group_id', flat=True)

    return user_group_queryset.values_list('id', flat=True)


def _get_access_group_lookup(model):
    model_field_names = {field.name for field in model._meta.get_fields()}

    if 'access_groups' in model_field_names:
        return 'access_groups'

    if 'document' in model_field_names:
        return 'document__access_groups'

    if 'document_file' in model_field_names:
        return 'document_file__document__access_groups'

    if 'document_version' in model_field_names:
        return 'document_version__document__access_groups'

    return None


def filter_queryset_for_user(queryset, user):
    """Restrict a queryset to objects the user can access."""
    if not getattr(user, 'is_authenticated', False):
        return queryset.none()

    if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
        return queryset

    access_group_lookup = _get_access_group_lookup(queryset.model)
    if not access_group_lookup:
        return queryset

    user_groups = _get_user_document_groups(user=user)
    if user_groups is None:
        return queryset.filter(**{'{}__isnull'.format(access_group_lookup): True}).distinct()

    return queryset.filter(
        Q(**{'{}__isnull'.format(access_group_lookup): True}) |
        Q(**{'{}__in'.format(access_group_lookup): user_groups})
    ).distinct()


def _resolve_document_object(view_instance, kwargs):
    document_id = (
        kwargs.get('pk') or kwargs.get('document_id') or
        kwargs.get('document_file_id') or kwargs.get('document_version_id')
    )
    if not document_id:
        return None

    queryset = None
    if view_instance is not None:
        if hasattr(view_instance, 'get_queryset'):
            try:
                queryset = view_instance.get_queryset()
            except Exception:
                queryset = None

        if queryset is None:
            queryset = getattr(view_instance, 'source_queryset', None)

        if queryset is None:
            queryset = getattr(view_instance, 'external_object_queryset', None)

    if queryset is None or not hasattr(queryset, 'filter'):
        return None

    return queryset.filter(pk=document_id).first()


def require_document_access(view_func):
    """Decorator to verify that the requested document is visible to the user."""

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not args:
            return view_func(*args, **kwargs)

        if hasattr(args[0], 'META'):
            request = args[0]
            view_instance = None
        else:
            view_instance = args[0]
            request = args[1] if len(args) > 1 else kwargs.get('request')

        if request is None:
            return view_func(*args, **kwargs)

        document = _resolve_document_object(view_instance=view_instance, kwargs=kwargs)
        if document is None:
            return view_func(*args, **kwargs)

        if not user_can_access_document(user=request.user, obj=document):
            raise Http404('Document not found or access denied.')

        return view_func(*args, **kwargs)

    return wrapper


class DocumentAccessMixin:
    """
    Mixin for viewsets to enforce document access cloisonnement.
    
    Automatically filters queryset by user's allowed_document_groups.
    """

    def get_queryset(self):
        """Filter queryset by user's document access groups."""
        parent = super()
        parent_any = parent  # type: Any
        if not hasattr(parent, 'get_queryset'):
            return []

        queryset = parent_any.get_queryset()
        request = getattr(self, 'request', None)
        user = getattr(request, 'user', None)

        if not user or not user.is_authenticated:
            return queryset.none()
        
        # If user is staff/superuser, no filtering
        if user.is_staff:
            return queryset
        
        # Admin users bypass cloisonnement
        if user.is_superuser:
            return queryset
        
        return filter_queryset_for_user(queryset=queryset, user=user)
    
    def check_object_permissions(self, request: Any, obj: Any):
        """Check user has access to specific object."""
        parent = super()
        parent_any = parent  # type: Any
        if hasattr(parent, 'check_object_permissions'):
            parent_any.check_object_permissions(request, obj)
        
        # Allow superusers and staff
        if request.user.is_staff or request.user.is_superuser:
            return
        
        if not user_can_access_document(user=request.user, obj=obj):
            from igar.core.audit import AuditLogger

            AuditLogger.log(
                action='document.access_denied',
                resource_type='document',
                resource_id=obj.id,
                user=request.user,
                ip_address=self._get_client_ip(request),
            )
            raise Http404('Document not found or access denied.')
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


def user_can_access_document(user, obj):
    """Return True when the user can access the object or its document root."""
    if not user or not getattr(user, 'is_authenticated', False):
        return False

    if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
        return True

    access_source = _resolve_access_source(obj=obj)

    if access_source is None or not hasattr(access_source, 'access_groups'):
        return True

    access_groups = access_source.access_groups.all()
    if not access_groups.exists():
        return True

    user_groups = _get_user_document_groups(user=user)
    if user_groups is None:
        return False

    return access_groups.filter(id__in=user_groups).exists()


def _resolve_access_source(obj):
    if hasattr(obj, 'access_groups'):
        return obj

    document = getattr(obj, 'document', None)
    if document is not None:
        return document

    document_file = getattr(obj, 'document_file', None)
    if document_file is not None:
        return getattr(document_file, 'document', None)

    document_version = getattr(obj, 'document_version', None)
    if document_version is not None:
        return getattr(document_version, 'document', None)

    return None


class IsDocumentAccessible(BasePermission):
    """
    Permission class to check document accessibility.
    
    Use with DetailViewset.check_object_permissions()
    """
    
    message = "Vous n'avez pas accès à ce document."

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:  # type: ignore[override]
        """Check if user can access document."""
        return user_can_access_document(user=request.user, obj=obj)
