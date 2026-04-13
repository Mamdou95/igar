"""Admin API URL routes for user/role management in Igar."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from igar.core.admin_views import (
    AdminPermissionsAPIView,
    AdminRolesViewSet,
    AdminUsersViewSet,
    AuditLogViewSet,
    DocumentAccessGroupViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', AdminUsersViewSet, basename='admin_users')
router.register(r'roles', AdminRolesViewSet, basename='admin_roles')
router.register(r'document-groups', DocumentAccessGroupViewSet, basename='admin_document_groups')
router.register(r'audit-logs', AuditLogViewSet, basename='admin_audit_logs')

app_name = 'admin'

urlpatterns = [
    path('permissions/', AdminPermissionsAPIView.as_view(), name='admin_permissions'),
    path('', include(router.urls)),
]
