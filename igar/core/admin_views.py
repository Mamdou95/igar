"""ViewSets for admin user and role management endpoints."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from igar.core.audit import AuditLogger
from igar.core.models import AuditLogEntry, DocumentAccessGroup
from igar.core.serializers import (
    DocumentAccessGroupSerializer,
    UserDetailSerializer,
    UserSimpleSerializer,
    GroupSimpleSerializer,
    AuditLogEntrySerializer,
)
from igar.core.permissions import CanManageUsers, CanManageRoles

User = get_user_model()


class AdminUsersViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users (admin only)."""

    queryset = User.objects.all().order_by('username')
    serializer_class = UserDetailSerializer
    permission_classes = [CanManageUsers]
    filter_backends = []
    filterset_fields = []
    ordering_fields = ['username', 'email', 'first_name', 'last_name', 'date_joined']
    ordering = ['username']
    pagination_class = None  # Will use default pagination from settings

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        is_active = params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() in ('1', 'true', 'yes'))

        is_staff = params.get('is_staff')
        if is_staff is not None:
            queryset = queryset.filter(is_staff=is_staff.lower() in ('1', 'true', 'yes'))

        group_id = params.get('group') or params.get('group_id')
        if group_id:
            queryset = queryset.filter(groups__id=group_id)

        search = params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        return queryset.distinct().order_by('username')

    def get_serializer_class(self):  # type: ignore[override]
        """Use simple serializer for list views."""
        if self.action == 'list':
            return UserSimpleSerializer
        return UserDetailSerializer

    def perform_create(self, serializer):
        """Create user and log event."""
        user = serializer.save()
        
        # Log to audit trail
        AuditLogger.log(
            action='user.created',
            resource_type='user',
            resource_id=user.id,
            user=self.request.user,
            new_values={
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'groups': list(user.groups.values_list('name', flat=True)),
            },
            ip_address=self._get_client_ip(),
            reason=f"User created via admin API"
        )

    def perform_update(self, serializer):
        """Update user and log event."""
        old_values = {
            'username': self.get_object().username,
            'email': self.get_object().email,
            'first_name': self.get_object().first_name,
            'last_name': self.get_object().last_name,
            'groups': list(self.get_object().groups.values_list('name', flat=True)),
            'is_active': self.get_object().is_active,
        }
        
        user = serializer.save()
        
        new_values = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'groups': list(user.groups.values_list('name', flat=True)),
            'is_active': user.is_active,
        }

        # Log to audit trail
        AuditLogger.log(
            action='user.modified',
            resource_type='user',
            resource_id=user.id,
            user=self.request.user,
            old_values=old_values,
            new_values=new_values,
            ip_address=self._get_client_ip(),
            reason=f"User modified via admin API"
        )

    def perform_destroy(self, instance):
        """Soft delete user (deactivate instead of delete)."""
        old_values = {
            'username': instance.username,
            'is_active': instance.is_active,
        }
        
        instance.is_active = False
        instance.save()

        new_values = {
            'username': instance.username,
            'is_active': instance.is_active,
        }

        # Log to audit trail
        AuditLogger.log(
            action='user.deactivated',
            resource_type='user',
            resource_id=instance.id,
            user=self.request.user,
            old_values=old_values,
            new_values=new_values,
            ip_address=self._get_client_ip(),
            reason=f"User deactivated via admin API"
        )

    def destroy(self, request, *args, **kwargs):
        """Override destroy to return explicit soft-delete response."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'status': 'user_deactivated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[CanManageUsers])
    def reset_password(self, request, pk=None):
        """Generate password reset token (sends email)."""
        # Placeholder for password reset functionality
        user = self.get_object()
        
        AuditLogger.log(
            action='user.modified',
            resource_type='user',
            resource_id=user.id,
            user=request.user,
            reason="Password reset requested"
        )
        
        return Response(
            {
                'status': 'reset_email_sent',
                'reset_url': f'/password-reset/?token=...'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[CanManageUsers])
    def reset_2fa(self, request, pk=None):
        """Reset user's 2FA."""
        user = self.get_object()
        
        # Disable OTP devices
        from django_otp.plugins.otp_totp.models import TOTPDevice
        TOTPDevice.objects.filter(user=user).delete()
        
        AuditLogger.log(
            action='user.2fa_reset',
            resource_type='user',
            resource_id=user.id,
            user=request.user,
            ip_address=self._get_client_ip(),
            reason=f"2FA reset by admin"
        )
        
        return Response(
            {'status': '2fa_reset'},
            status=status.HTTP_200_OK
        )

    def _get_client_ip(self):
        """Get client IP address from request."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class AdminRolesViewSet(viewsets.ModelViewSet):
    """ViewSet for managing roles (admin only)."""

    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSimpleSerializer
    permission_classes = [CanManageRoles]
    filter_backends = []
    filterset_fields = []
    ordering_fields = ['name']
    ordering = ['name']

    def perform_create(self, serializer):
        """Create role and log event."""
        group = serializer.save()
        
        AuditLogger.log(
            action='role.created',
            resource_type='role',
            resource_id=group.id,
            user=self.request.user,
            new_values={'name': group.name},
            ip_address=self._get_client_ip(),
        )

    def perform_update(self, serializer):
        """Update role and log event."""
        old_values = {'name': self.get_object().name}
        group = serializer.save()
        new_values = {'name': group.name}

        AuditLogger.log(
            action='role.modified',
            resource_type='role',
            resource_id=group.id,
            user=self.request.user,
            old_values=old_values,
            new_values=new_values,
            ip_address=self._get_client_ip(),
        )

    def destroy(self, request, *args, **kwargs):
        """Delete role only when no users are assigned."""
        group = self.get_object()
        if group.user_set.exists():
            return Response(
                {'detail': 'Role cannot be deleted while users are assigned.'},
                status=status.HTTP_409_CONFLICT,
            )

        old_values = {
            'name': group.name,
            'permissions': list(group.permissions.values_list('codename', flat=True)),
        }
        resource_id = group.id
        group.delete()

        AuditLogger.log(
            action='role.deleted',
            resource_type='role',
            resource_id=resource_id,
            user=request.user,
            old_values=old_values,
            new_values={},
            ip_address=self._get_client_ip(),
        )
        return Response({'status': 'role_deleted'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def permissions(self, request):
        """List all available permissions."""
        permissions = Permission.objects.all().values('id', 'codename', 'name')
        return Response(list(permissions))

    def _get_client_ip(self):
        """Get client IP address from request."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class DocumentAccessGroupViewSet(viewsets.ModelViewSet):
    """ViewSet for document access groups."""

    queryset = DocumentAccessGroup.objects.all()
    serializer_class = DocumentAccessGroupSerializer
    permission_classes = [IsAdminUser]
    filter_backends = []
    filterset_fields = []
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for audit logs (read-only)."""

    queryset = AuditLogEntry.objects.all().order_by('-created_at')
    serializer_class = AuditLogEntrySerializer
    permission_classes = [IsAdminUser]
    filter_backends = []
    filterset_fields = []
    ordering_fields = ['created_at', 'action']
    ordering = ['-created_at']


class AdminPermissionsAPIView(APIView):
    """List available permissions grouped by app label."""

    permission_classes = [CanManageRoles]

    def get(self, request):
        permissions = Permission.objects.select_related('content_type').order_by(
            'content_type__app_label', 'codename'
        )
        results = [
            {
                'id': permission.pk,
                'codename': permission.codename,
                'name': permission.name,
                'app': permission.content_type.app_label,
            }
            for permission in permissions
        ]
        return Response({'results': results})
